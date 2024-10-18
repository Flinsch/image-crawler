from image_crawler import ImageCrawler

image_crawler = ImageCrawler()
result = image_crawler.crawl_recursive('https://www.meine-domain.de/')

print('')
print('Image count: ' + str(result['image_count']))
print('Total size (bytes): ' + str(result['total_size_bytes']))
