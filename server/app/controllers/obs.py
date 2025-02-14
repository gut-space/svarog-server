from flask import abort, render_template

from app import app
from app.repository import ObservationId, Repository, Observation
from app.pagination import use_pagination
from math import floor
from app.utils import strfdelta
from flask_login import current_user

# from tletools import TLE
from pyorbital.orbital import Orbital, A as EARTH_RADIUS
from astropy import units as u
import os


@app.route('/obs/<obs_id>')
@use_pagination(5)
def obs(obs_id: ObservationId = None, limit_and_offset=None):
    if obs_id is None:
        abort(300, description="ID is required")
        return

    repository = Repository()
    with repository.transaction():
        observation = repository.read_observation(obs_id)

        orbit = None

        if observation is None:
            abort(404, "Observation not found")

        files = repository.read_observation_files(observation["obs_id"],
                                                  **limit_and_offset)
        files_count = repository.count_observation_files(obs_id)
        satellite = repository.read_satellite(observation["sat_id"])

        orbit = observation
        if observation['tle'] is not None:
            # observation['tle'] is always an array of exactly 2 strings.
            orbit = parse_tle(*observation['tle'], satellite["sat_name"])

        station = repository.read_station(observation["station_id"])

    # Now tweak some observation parameters to make them more human readable
    observation = human_readable_obs(observation)

    # Now determine if there is a logged user and if there is, if this user is the owner of this
    # station. If he is, we should show the admin panel.
    user_id = 0
    owner = False
    if current_user.is_authenticated:
        user_id = current_user.get_id()

        # Check if the current user is the owner of the station.
        station_id = station['station_id']

        owner = repository.is_station_owner(user_id, station_id)

    return 'obs.html', dict(obs=observation, files=files,
                            sat_name=satellite["sat_name"], item_count=files_count, orbit=orbit, station=station, is_owner=owner)


def calculate_orbit_parameters(perigee: float, eccentricity: float, earth_radius: float = 0):
    """
    Calculates the semi-major axis and apogee.

    Parameters:
        perigee (float): The perigee distance. If using altitude, pass the altitude.
        eccentricity (float): The orbit's eccentricity.
        earth_radius (float): (Optional) Earth's radius to add to the altitude.
                                Defaults to 0 if perigee is already the distance from the center.

    Returns:
        tuple: (semi_major_axis, apogee)
    """
    # If perigee is provided as altitude, convert it to distance from the center
    r_p = perigee + earth_radius

    # Calculate the semi-major axis using r_p = a (1 - e)
    a = r_p / (1 - eccentricity)

    # Calculate the apogee: r_a = a (1 + e)
    r_a = a * (1 + eccentricity)

    return a, r_a


def parse_tle(tle1: str, tle2: str, name: str) -> dict:
    """ Parses orbital data in TLE format and returns a dictionary with printable orbital elements
        and other parameters."""

    # Create Orbital object from TLE data
    orb = Orbital(name, line1=tle1, line2=tle2)

    # Get orbital elements
    elements = orb.orbit_elements

    print(f"#### elements: {elements}")
    from pprint import pprint
    pprint(vars(elements))

    # Calculate period in minutes and seconds
    period_minutes = elements.period  # Period is returned in minutes
    m = floor(period_minutes)
    s = (period_minutes - m) * 60

    # Calculate apogee and perigee (in km)
    perigee = float(elements.perigee) # Already in km above Earth's surface
    semi_major, apogee = calculate_orbit_parameters(perigee, elements.excentricity, EARTH_RADIUS)

    # Format the orbital parameters
    orb_dict = {}
    orb_dict["overview"] = f"Satellite {name} at {apogee:.1f}km x {perigee:.1f}km"
    orb_dict["inc"] = f"{elements.inclination:.1f} deg"
    orb_dict["ecc"] = elements.excentricity
    orb_dict["a"] = semi_major   # in km above the center of the earth
    orb_dict["r_a"] = f"{(apogee - EARTH_RADIUS):.1f} km above surface"
    orb_dict["r_p"] = f"{(perigee):.1f} km above surface"
    orb_dict["raan"] = f"{elements.right_ascension:.1f} deg"
    orb_dict["period"] = f"{period_minutes:.1f} min ({m}m {int(s)}s)"
    orb_dict["epoch"] = str(elements.epoch) + " UTC"  # orb.tle.epoch.strftime("%Y-%m-%d %H:%M:%S") + " UTC"

    return orb_dict


def human_readable_obs(obs: Observation) -> Observation:
    """Gets an observation and formats some of its parameters to make it more human readable.
       Returns an observation."""

    aos_los_duration = obs["los"] - obs["aos"]
    tca_correction = ""

    if obs["aos"] == obs["tca"]:
        obs["tca"] = obs["aos"] + aos_los_duration / 2
        tca_correction = " (corrected, the original observation record incorrectly says TCA = AOS)"

    aos_tca_duration = obs["tca"] - obs["aos"]

    if "config" in obs and obs['config'] and "recipe" in obs["config"] and "<function execute" in obs["config"]["recipe"]:
        obs["config"]["recipe"] = "unknown (not recorded properly)"

    obs.aos = obs["aos"].strftime("%Y-%m-%d %H:%M:%S")
    obs.tca = obs["tca"].strftime("%Y-%m-%d %H:%M:%S") + ", " + strfdelta(aos_tca_duration, fmt="{M:02}m {S:02}s since AOS") + tca_correction
    obs.los = obs["los"].strftime("%Y-%m-%d %H:%M:%S") + ", " + strfdelta(aos_los_duration, fmt="{M:02}m {S:02}s since AOS")
    return obs


@app.route('/obs/delete/<obs_id>', methods=["GET", "POST"])
def obs_delete(obs_id: ObservationId = None):

    # First check if such an observation even exists.
    repository = Repository()
    observation = repository.read_observation(obs_id)
    if observation is None:
        return render_template('obs_delete.html', status=["There is no observation %s" % obs_id], obs_id=obs_id)

    # Second, check if the guy is logged in.
    if not current_user.is_authenticated:
        return render_template('obs_delete.html', status=["You are not logged in, you can't delete anything."], obs_id=obs_id)

    # Ok, at least this guy is logged in. Let's check who he is.
    user_id = current_user.get_id()

    # Check if the current user is the owner of the station.
    station = repository.read_station(observation["station_id"])
    station_id = station['station_id']

    owner = repository.is_station_owner(user_id, station_id)

    if not owner:
        return render_template('obs_delete.html', status=["You are not the owner of station %s, you can't delete observation %s."
                                                          % (station.name, obs_id)], obs_id=obs_id)

    # If you got that far, this means the guy is logged in, he's the owner and is deleting his own observation.

    status = obs_delete_db_and_disk(repository, obs_id)
    return render_template('obs_delete.html', status=status, obs_id=obs_id)


def obs_delete_db_and_disk(repository: Repository, obs_id: ObservationId):

    app.logger.info("About to delete observation %s and all its files" % obs_id)

    # Step 1: Create a list of files to be deleted. There may be several products.
    products = repository.read_observation_files(obs_id)
    obs = repository.read_observation(obs_id)
    files = [[f['filename'], "product"] for f in products]

    # Step 2: thumbnail is stored with the observation. There's at most one thumbnail.
    files.append([os.path.join("thumbs", obs['thumbnail']), "thumbnail"])

    # Step 3: And there are two charts: alt-az pass chart and polar pass chart.
    files.append([os.path.join("charts", "by_time-%s.png" % obs_id), "pass chart"])
    files.append([os.path.join("charts", "polar-%s.png" % obs_id), "polar pass chart"])

    # All those files are stored in this dir
    root = app.config["storage"]['image_root']

    status = []
    for f in files:
        path = os.path.join(root, f[0])
        app.logger.info("Trying to delete [%s]" % path)
        try:
            os.remove(path)
            status.append("Deleted %s file %s." % (f[1], f[0]))
        except Exception as ex:
            status.append("Failed to delete %s file: %s, reason: %s" % (f[1], path, repr(ex)))

    # Step 4: delete entries in the db
    repository.delete_observation(obs_id)
    status.append("DB removal complete.")

    return status
