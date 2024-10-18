import requests
import re

class ImageCrawler:
    def crawl(self, url: str):
        match = re.search(r'^(https?)://([^\s/]+)(/[^?]*)?', url)
        if not match:
            print(f'The URL could not be parsed into its components: {url}')
            return None

        protocol = match.group(1)
        domain = match.group(2)
        base_path = match.group(3).rstrip('/')

        print('')
        print(f'Crawling URL: {protocol}://{domain}{base_path}')
        print('')

        result = {
            'protocol': protocol,
            'domain': domain,
            'base_path': base_path,
            'response_text': None,
            'image_count': 0,
            'total_size_bytes': 0,
        }

        response = requests.get(url, allow_redirects=True)
        result['response_text'] = response.text

        image_urls = re.findall(r'<img[^>]+src="([^"?]+?\.(?:jpg|jpeg|png|gif))(?:\?[^"]*)?"', result['response_text'], flags=re.IGNORECASE)
        image_urls += re.findall(r'<a[^>]+href="([^"?]+?\.(?:jpg|jpeg|png|gif))(?:\?[^"]*)?"', result['response_text'], flags=re.IGNORECASE)

        for image_url in image_urls:
            image_url = self.__url(protocol, domain, '', image_url)
            if not image_url:
                continue

            response = requests.head(image_url, allow_redirects=True)
            size_bytes = int(response.headers.get('Content-Length', 0))
            if size_bytes == 0:
                response = requests.get(image_url, allow_redirects=True)
                size_bytes = len(response.content)

            print(size_bytes, image_url)

            result['image_count'] += 1
            result['total_size_bytes'] += size_bytes

        return result

    def crawl_recursive(self, url: str, ignore: set = set()):
        if url in ignore:
            return None
        ignore.add(url)

        result = self.crawl(url)
        if not result:
            return None

        protocol = result['protocol']
        domain = result['domain']
        base_path = result['base_path']

        link_urls = re.findall(r'<a[^>]+href="(.*?)"', result['response_text'])

        for link_url in link_urls:
            link_url = self.__url(protocol, domain, '', link_url)
            if not link_url:
                continue

            temp = self.crawl_recursive(link_url, ignore)
            if not temp:
                continue

            result['image_count'] += temp['image_count']
            result['total_size_bytes'] += temp['total_size_bytes']

        return result

    def __url(self, protocol: str, domain: str, base_path: str, url: str) -> str | None:
        match = re.search(domain + base_path.rstrip('/') + '(/.*)', url)
        if not match:
            return None
        path = match.group(1)
        return protocol + '://' + domain + base_path.rstrip('/') + path
