
# qBitrr

[![PyPI - License](https://img.shields.io/pypi/l/qbitrr)](https://github.com/Feramance/Qbitrr/blob/master/LICENSE)
[![Pulls](https://img.shields.io/docker/pulls/feramance/qbitrr.svg)](https://hub.docker.com/r/feramance/qbitrr)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qbitrr)
![Platforms](https://img.shields.io/badge/platform-linux--64%20%7C%20osx--64%20%7C%20win--32%20%7C%20win--64-lightgrey)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Feramance/qBitrr/master.svg)](https://results.pre-commit.ci/latest/github/Feramance/qBitrr/master)
[![CodeQL](https://github.com/Feramance/qBitrr/actions/workflows/codeql.yml/badge.svg?branch=master)](https://github.com/Feramance/qBitrr/actions/workflows/codeql.yml)
[![Create a Release](https://github.com/Feramance/qBitrr/actions/workflows/release.yml/badge.svg?branch=master)](https://github.com/Feramance/qBitrr/actions/workflows/release.yml)

[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A simple script to monitor [qBit](https://github.com/qbittorrent/qBittorrent) and communicate with [Radarr](https://github.com/Radarr/Radarr) and [Sonarr](https://github.com/Sonarr/Sonarr)

## Features

- Monitor qBit for Stalled/bad entries and delete them then blacklist them on Arrs (Option to also trigger a re-search action).
- Monitor qBit for completed entries and tell the appropriate Arr instance to import it:
  - `qbitrr DownloadedMoviesScan` for Radarr
  - `qbitrr DownloadedEpisodesScan` for Sonarr
- Skip files in qBit entries by extension, folder or regex.
- Monitor completed folder and clean it up.
- Usage of [ffprobe](https://github.com/FFmpeg/FFmpeg) to ensure downloaded entries are valid media.
- Trigger periodic Rss Syncs on the appropriate Arr instances.
- Trigger Queue update on appropriate Arr instances.
- Search requests from [Overseerr](https://github.com/sct/overseerr) or [Ombi](https://github.com/Ombi-app/Ombi).
- Auto add/remove trackers
- Set per tracker values
- **Sonarr v4 support**
- Available if provided with a Sonarr/Radarr database file:
  - Monitor Arr's databases to trigger missing episode searches.
  - Customizable year range to search for (at a later point will add more option here, for example search whole series/season instead of individual episodes, search by name, category etc).

## Tested with

Some things to know before using it.

- qBittorrent 4.5.x
- [Sonarr](https://github.com/Sonarr/Sonarr) and [Radarr](https://github.com/Radarr/Radarr) both setup to add tags to all downloads.
- qBit set to create sub-folders for tag.

## Usage
### Native

***PyPI package is outdated, please use the docker image or download the latest release!***

1. Download the latest release
2. Run `qbitrr` to generate a config file
3. Edit the config file (located at `~/config/config.toml` (~ is your current directory)
4. Run `qbitrr` again to start the script

***There is no auto-update feature, you will need to manually download the latest release and replace the old one.***

### Docker

The docker image can be found [here](https://hub.docker.com/r/feramance/qbitrr)

#### Docker Image

- The docker image can be found [here](https://hub.docker.com/r/feramance/qbitrr)

#### Docker Run

```bash
docker run -d \
  --name=qbitrr \
  -e TZ=Europe/London \
  -v /etc/localtime:/etc/localtime:ro \
  -v /path/to/appdata/qbitrr:/config \
  -v /path/to/sonarr/db:/databases/sonarr.db:ro \
  -v /path/to/radarr/db:/databases/radarr.db:ro \
  -v /path/to/completed/downloads/folder:/completed_downloads:rw \
  --restart unless-stopped \
  feramance/qbitrr
```

#### Docker Compose

```yaml
version: "3"
services:
  qbitrr:
    image: feramance/qbitrr
    user: 1000:1000 # Required to ensure teh container is run as the user who has perms to see the 2 mount points and the ability to write to the CompletedDownloadFolder mount
    tty: true # Ensure the output of docker-compose logs qbitrr are properly colored.
    restart: unless-stopped
    # networks: This container MUST share a network with your Sonarr/Radarr instances
    environment:
      - TZ=Europe/London
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /path/to/appdata/qbitrr:/config  # Config folder for qbitrr
      - /path/to/sonarr/db:/sonarr.db:ro # This is only needed if you want episode search handling :ro means it is only ever mounted as a read-only folder, the script never needs more than read access
      - /path/to/radarr/db:/radarr.db:ro # This is only needed if you want movie search handling, :ro means it is only ever mounted as a read-only folder, the script never needs more than read access
      - /path/to/completed/downloads/folder:/completed_downloads:rw # The script will ALWAYS require write permission in this folder if mounted, this folder is used to monitor completed downloads and if not present will cause the script to ignore downloaded file monitoring.
      # Now just to make sure it is clean, when using this script in a docker you will need to ensure you config.toml values reflect the mounted folders.#
      # For example, for your Sonarr.DatabaseFile value using the values above you'd add
      # DatabaseFile = /sonarr.db/path/in/container/sonarr.db
      # Because this is where you mounted it to
      # The same would apply to Settings.CompletedDownloadFolder
      # e.g CompletedDownloadFolder = /completed_downloads/folder/in/container

    logging: # this script will generate a LOT of logs - so it is up to you to decide how much of it you want to store
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: 3
    depends_on: # Not needed but this ensures qBitrr only starts if the dependencies are up and running
      - qbittorrent
      - radarr-1080p
      - radarr-4k
      - sonarr-1080p
      - sonarr-anime
      - overseerr
```

##### Important mentions for docker

- The script will always expect a completed config.toml file
- When you first start the container a "config.rename_me.toml" will be added to `/path/to/appdata/qbitrr`
  - Make sure to rename it to 'config.toml' then edit it to your desired values
