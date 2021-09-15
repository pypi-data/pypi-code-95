# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import numpy as np
import scrapy


class ImagesItem(scrapy.Item):

    url = scrapy.Field()
    images_url = scrapy.Field()

    def extract_clean_imgs(self, imgs):
        """
        Extract images urls without duplicates and with only three
         extentions (i.e., GIF, PNG, JPEG)

        :param response: Object
            An HTTP response
        :return:
        """
        try:

            # filter images according to their extension using vectorized
            # fast operations
            mask = [(".gif" in img or ".png" in img or ".jpeg" in img) and "http" in img
                    for img in imgs]

            mask = np.asarray(mask)

            imgs = np.unique(imgs[mask])

            if len(imgs) > 1:

                return imgs.tolist()

        except:

            return None

        return None
