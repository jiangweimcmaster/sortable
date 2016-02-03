import sys
import json
import re

class Product(object):

    def __init__(self, product_name, manufacturer, model, date, family=None):
        self.product_name = product_name
        self.manufacturer = manufacturer
        self.model = model
        self.date = date
        self.family = family

class Listing(object):

    def __init__(self, title, manufacturer, currency, price):
        self.title = title
        self.manufacturer = manufacturer
        self.currency = currency
        self.price = price

    def toDict(self):
        return {'title': self.title, 'manufacturer': self.manufacturer, 'currency': self.currency, 'price': self.price}

class Searching(object):

    def __init__(self, products_file, listings_file):
        self.products = self.loadProducts(products_file)
        self.listings = self.loadListings(listings_file)

    def loadProducts(self, file):
        result = []
        with open(file, 'r') as f:
            for line in f:
                json_object = json.loads(line)
                product_name = json_object['product_name']
                manufacturer = json_object['manufacturer']
                model = json_object['model']
                date = json_object['announced-date']
                if 'family' in json_object:
                    family = json_object['family']
                    result.append(Product(product_name, manufacturer, model, date, family))
                else:
                    result.append(Product(product_name, manufacturer, model, date))
        return result

    def loadListings(self, file):
        result = []
        with open(file, 'r') as f:
            for line in f:
                json_object = json.loads(line)
                result.append(Listing(json_object['title'], json_object['manufacturer'],
                                      json_object['currency'], json_object['price']))
        return result

    def match_products(self, listing):
        # giving a listing to see if there are products matching
        # first check if manufacturers (company name) of listing and product are same
        # then check if product's model and/or family (if applicable) are in listing's title
        # I lowercase all names to find more matchings
        matched_products = []
        l_title = listing.title.lower()
        l_company = listing.manufacturer.lower()
        for product in self.products:
            p_company = product.manufacturer.lower()
            p_model = product.model.lower()
            if p_company in l_title or p_company in l_company:
                if (product.family and p_model in l_title and product.family.lower() in l_title) \
                        or p_model in l_title:
                    matched_products.append(product)
        return matched_products

    def searching_listings(self):
        # run self.match_products() on every listing
        print "Starting..."
        product_results = {}

        for listing in self.listings:
            matched_products = self.match_products(listing)
            for product in matched_products:
                name = product.product_name
                if name not in product_results:
                    product_results[name] = []
                product_results[name].append(listing.toDict())
        return product_results

    def output(self, file):
        result = self.searching_listings()
        print "Writing to " + file + "..."
        with open(file, 'w') as o:
            num = 0
            for product in self.products:
                matched_listings = result.get(product.product_name, [])
                num += len(matched_listings)
                dict = {'product_name': product.product_name, 'listings': matched_listings}
                o.write(json.dumps(dict)+"\n")
        print "Done"
        print "Total found matches: " + str(num)



if __name__ == '__main__':
    search = Searching("products.txt", "listings.txt")
    search.output("results.txt")