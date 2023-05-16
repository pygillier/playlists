from flask import current_app


class M3U:

    @staticmethod
    def convert(tracks) -> str:
        current_app.logger.debug("Converting list to M3U playlist")

        pls = ["#EXTM3U", "#EXTENC: UTF-8", ""]

        for track in tracks:
            artists = [a["name"] for a in track["track"]["artists"]]

            pls.append("#EXTINF:{},{} - {}".format(
                round(track["track"]["duration_ms"] / 1000),
                ", ".join(artists),
                track["track"]["name"]
            ))
            song_url = track["track"]["preview_url"] \
                if track["track"]["preview_url"] is not None \
                else track["track"]["external_urls"]["spotify"]

            pls.append(song_url)

        return "\n".join(pls)
