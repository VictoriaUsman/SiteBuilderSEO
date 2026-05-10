from pathlib import Path
from wordpress.client import WordPressClient


def upload_image(client: WordPressClient, image_path: Path, alt_text: str) -> int | None:
    if not image_path or not image_path.exists():
        return None

    with open(image_path, "rb") as f:
        image_data = f.read()

    resp = client.session.post(
        client._api("media"),
        data=image_data,
        headers={
            "Content-Type": "image/jpeg",
            "Content-Disposition": f'attachment; filename="{image_path.name}"',
        },
        timeout=60,
    )
    resp.raise_for_status()
    media = resp.json()

    # Set alt text via update
    client.session.post(
        client._api(f"media/{media['id']}"),
        json={"alt_text": alt_text, "caption": alt_text},
        timeout=15,
    )

    return media["id"]
