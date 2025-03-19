import concurrent.futures
import multiprocessing
import os
from urllib.parse import unquote, urlparse

import requests
from tqdm import tqdm


def download_file(url, folder_path, timeout=30):
    """
    Download a file from the given URL to the specified folder

    Args:
        url (str): URL of the file to download
        folder_path (str): Path to the folder where the file should be saved
        timeout (int): Timeout for the request in seconds

    Returns:
        str: Path to the downloaded file or None if download failed
    """
    try:
        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(unquote(parsed_url.path))

        # If no filename could be extracted, use the last part of the URL
        if not filename:
            filename = url.split("/")[-1]

        # If still no filename, use a default name
        if not filename:
            filename = "downloaded_file"

        file_path = os.path.join(folder_path, filename)

        # Send a request to get the file with timeout
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Get the total file size if available
        total_size = int(response.headers.get("content-length", 0))

        # Download the file with progress bar
        with (
            open(file_path, "wb") as file,
            tqdm(
                desc=filename,
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar,
        ):
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    file.write(chunk)
                    bar.update(len(chunk))

        return file_path

    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None
    except requests.Timeout:
        print(f"Timeout error downloading {url}")
        return None


def download_files_parallel(urls, folder_path, max_workers=None):
    """
    Download multiple files in parallel

    Args:
        urls (list): List of URLs to download
        folder_path (str): Path to the folder where files should be saved
        max_workers (int, optional): Maximum number of parallel downloads.
                                    If None, will use CPU count * 2 or 32, whichever is smaller.

    Returns:
        list: Paths to successfully downloaded files
    """
    # Determine optimal number of workers if not specified
    if max_workers is None:
        # Get CPU count and use a reasonable multiple (typically 2-5x for IO-bound tasks)
        cpu_count = multiprocessing.cpu_count()

        # For IO-bound operations like downloads, we can use more workers than CPU cores
        max_workers = min(
            cpu_count * 2, 32
        )  # Limit to 32 to avoid overwhelming the system
        print(f"Using {max_workers} workers based on {cpu_count} CPU cores")

    downloaded_files = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_url = {
            executor.submit(download_file, url, folder_path): url for url in urls
        }

        # Process completed downloads
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                file_path = future.result()
                if file_path:
                    downloaded_files.append(file_path)
                    print(f"Successfully downloaded: {file_path}")
            except Exception as e:
                print(f"Download failed for {url}: {e}")

    return downloaded_files


if __name__ == "__main__":
    # Example usage
    image_urls = [
        "https://images.unsplash.com/photo-1726138400966-63461367804d?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    ]

    download_folder = "downloads"

    print(f"Starting download of {len(image_urls)} files to '{download_folder}' folder")
    downloaded = download_files_parallel(image_urls, download_folder)
    print(f"Downloaded {len(downloaded)} files successfully")
