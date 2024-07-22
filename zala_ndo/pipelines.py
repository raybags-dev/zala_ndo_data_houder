from itemadapter import ItemAdapter
import sqlite3


class ZalaNdoPipeline:
    def process_item(self, item, spider):
        return item


class SQLiteNoDupesPipeline:
    def __init__(self):
        self.con = sqlite3.connect("products.db")
        self.cur = self.con.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products(
                uuid TEXT, 
                name TEXT, 
                colour TEXT, 
                image TEXT, 
                manufacturer TEXT, 
                sku TEXT, 
                description TEXT, 
                variant_sku TEXT PRIMARY KEY, 
                availability TEXT, 
                price TEXT, 
                url TEXT, 
                product_id TEXT
            )
            """
        )
        self.con.commit()

    def process_item(self, item, spider):
        try:
            self.cur.execute(
                """SELECT * FROM products WHERE variant_sku = ? """,
                (item["variant_sku"],),
            )
            result = self.cur.fetchone()
            if result:
                spider.logger.warn(
                    f"Item already exists in <products> DB, {item['variant_sku']}"
                )
            else:
                self.cur.execute(
                    """
                    INSERT INTO products(
                        uuid, 
                        name, 
                        colour, 
                        image, 
                        manufacturer, 
                        sku, 
                        description, 
                        variant_sku, 
                        availability, 
                        price, 
                        url, 
                        product_id
                    ) 
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        item["uuid"],
                        item["name"],
                        item["colour"],
                        item["image"],
                        item["manufacturer"],
                        item["sku"],
                        item["description"],
                        item["variant_sku"],
                        item["availability"],
                        item["price"],
                        item["url"],
                        item["product_id"],
                    ),
                )
                self.con.commit()
        except sqlite3.Error as e:
            spider.logger.error(f"Error processing item: {e}")
        return item

    def close_spider(self, spider):
        self.con.close()
