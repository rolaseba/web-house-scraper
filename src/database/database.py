"""
Database module for storing property data in SQLite.
Creates and manages the properties table based on configured fields.
"""

import sqlite3
import logging
from typing import Dict, Any, List
from src.utils import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PropertyDatabase:
    """SQLite database manager for property listings."""
    
    def __init__(self, db_file: str = None):
        self.db_file = db_file or config.DATABASE_FILE
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_table()
    
    def _connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_file}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _get_field_type(self, field_name: str) -> str:
        """Determine SQLite data type for a field based on its name."""
        if field_name in ["metros_cuadrados_cubiertos", "metros_cuadrados_totales", 
                         "cantidad_dormitorios", "cantidad_banos", "cantidad_ambientes"]:
            return "INTEGER"
        elif field_name == "precio":
            return "REAL"
        elif field_name in ["tiene_patio", "tiene_quincho", "tiene_pileta", "tiene_cochera",
                           "tiene_balcon", "tiene_terraza"]:
            return "BOOLEAN"
        else:
            return "TEXT"
    
    def _create_table(self):
        """Create the properties table if it doesn't exist."""
        # Start with id and url
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT", "url TEXT UNIQUE NOT NULL"]
        
        # Add configured fields
        for field in config.EXTRACTION_FIELDS:
            field_type = self._get_field_type(field)
            columns.append(f"{field} {field_type}")
        
        # Add timestamp
        columns.append("scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS properties (
            {', '.join(columns)}
        )
        """
        
        try:
            self.cursor.execute(create_table_sql)
            self.conn.commit()
            logger.info("Properties table created/verified")
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            raise
    
    def upsert_property(self, data: Dict[str, Any]) -> str:
        """
        Insert or update a property in the database (UPSERT).
        Returns 'inserted', 'updated', or 'error'.
        """
        url = data.get("url")
        
        # Check if property already exists
        existing = self.get_property_by_url(url)
        
        if existing:
            # UPDATE existing property
            try:
                # Build UPDATE statement
                set_clauses = []
                values = []
                
                for field in config.EXTRACTION_FIELDS:
                    if field in data:
                        set_clauses.append(f"{field} = ?")
                        values.append(data[field])
                
                # Add URL for WHERE clause
                values.append(url)
                
                update_sql = f"""
                UPDATE properties 
                SET {', '.join(set_clauses)}, scraped_at = CURRENT_TIMESTAMP
                WHERE url = ?
                """
                
                self.cursor.execute(update_sql, values)
                self.conn.commit()
                
                logger.info(f"🔄 Updated property: {url}")
                return 'updated'
                
            except Exception as e:
                logger.error(f"Failed to update property: {e}")
                logger.error(f"Data: {data}")
                raise
        else:
            # INSERT new property
            try:
                # Prepare columns and values
                columns = ["url"]
                values = [url]
                placeholders = ["?"]
                
                for field in config.EXTRACTION_FIELDS:
                    if field in data:
                        columns.append(field)
                        values.append(data[field])
                        placeholders.append("?")
                
                insert_sql = f"""
                INSERT INTO properties ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                """
                
                self.cursor.execute(insert_sql, values)
                self.conn.commit()
                
                logger.info(f"✓ Inserted new property: {url}")
                return 'inserted'
                
            except Exception as e:
                logger.error(f"Failed to insert property: {e}")
                logger.error(f"Data: {data}")
                raise
    
    # Keep old method for backward compatibility
    def insert_property(self, data: Dict[str, Any]) -> bool:
        """
        Legacy method - now calls upsert_property.
        Returns True if successful.
        """
        result = self.upsert_property(data)
        return result in ['inserted', 'updated']
    
    def get_all_properties(self) -> List[Dict[str, Any]]:
        """Retrieve all properties from the database."""
        try:
            self.cursor.execute("SELECT * FROM properties")
            rows = self.cursor.fetchall()
            
            # Get column names
            columns = [description[0] for description in self.cursor.description]
            
            # Convert to list of dictionaries
            properties = []
            for row in rows:
                properties.append(dict(zip(columns, row)))
            
            return properties
        except Exception as e:
            logger.error(f"Failed to retrieve properties: {e}")
            raise
    
    def get_property_by_url(self, url: str) -> Dict[str, Any]:
        """Get a specific property by URL."""
        try:
            self.cursor.execute("SELECT * FROM properties WHERE url = ?", (url,))
            row = self.cursor.fetchone()
            
            if row:
                columns = [description[0] for description in self.cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve property: {e}")
            raise
    
    def count_properties(self) -> int:
        """Count total properties in database."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM properties")
            count = self.cursor.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"Failed to count properties: {e}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def test_database():
    """Test the database module."""
    with PropertyDatabase("test_properties.db") as db:
        # Test data
        test_property = {
            "url": "https://example.com/test-property",
            "tipo_operacion": "venta",
            "direccion": "Av. Test 123",
            "barrio": "Centro",
            "metros_cuadrados_cubiertos": 80,
            "metros_cuadrados_totales": 100,
            "precio": 150000,
            "moneda": "USD",
            "cantidad_dormitorios": 3,
            "cantidad_banos": 2,
            "tiene_patio": True,
            "tiene_quincho": False,
            "tiene_pileta": False,
            "tiene_cochera": True,
            "antiguedad": "10 años",
            "descripcion_breve": "Hermosa casa en el centro"
        }
        
        # Insert
        success = db.insert_property(test_property)
        print(f"Insert successful: {success}")
        
        # Count
        count = db.count_properties()
        print(f"Total properties: {count}")
        
        # Retrieve
        property_data = db.get_property_by_url(test_property["url"])
        print(f"Retrieved property: {property_data}")


if __name__ == "__main__":
    test_database()
