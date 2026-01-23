"""
Mock Koha API client for testing without a live server.
Provides realistic sample data for demonstration purposes.
"""

import asyncio
import random
from typing import Dict, List, Optional, Tuple

from .client import BiblioRecord, HoldingItem, SearchResult, KohaAPIClient
from utils.config import KohaConfig


# Sample book data for testing
SAMPLE_BOOKS = [
    {
        "biblio_id": 1,
        "title": "For Whom the Bell Tolls",
        "author": "Hemingway, Ernest, 1899-1961",
        "publication_year": "1940",
        "publisher": "Charles Scribner's Sons",
        "isbn": "9780684803357",
        "item_type": "Book",
        "call_number": "PS3515.E37 F6",
        "call_number_lcc": "PS3515.E37 F6",
        "call_number_dewey": "813.52",
        "summary": "A young American in the International Brigades during the Spanish Civil War.",
    },
    {
        "biblio_id": 2,
        "title": "True at First Light",
        "author": "Hemingway, Ernest, 1899-1961",
        "publication_year": "1999",
        "publisher": "Scribner",
        "isbn": "9780684842714",
        "item_type": "Book",
        "call_number": "PS3515.E37 T78",
        "call_number_lcc": "PS3515.E37 T78",
        "call_number_dewey": "813.52",
        "summary": "A fictionalized memoir of an African safari.",
    },
    {
        "biblio_id": 3,
        "title": "The Old Man and the Sea",
        "author": "Hemingway, Ernest, 1899-1961",
        "publication_year": "1952",
        "publisher": "Charles Scribner's Sons",
        "isbn": "9780684801223",
        "item_type": "sound recording",
        "call_number": "PS3515.E37 O4",
        "call_number_lcc": "PS3515.E37 O4",
        "call_number_dewey": "813.52",
        "summary": "The story of an aging Cuban fisherman and his epic battle with a giant marlin.",
    },
    {
        "biblio_id": 4,
        "title": "A Moveable Feast",
        "author": "Hemingway, Ernest, 1899-1961",
        "publication_year": "1964",
        "publisher": "Charles Scribner's Sons",
        "isbn": "9780684824994",
        "item_type": "Book",
        "call_number": "PS3515.E37 Z523",
        "call_number_lcc": "PS3515.E37 Z523",
        "call_number_dewey": "813.52",
        "summary": "A memoir of Paris in the 1920s.",
    },
    {
        "biblio_id": 5,
        "title": "Foundation",
        "author": "Asimov, Isaac, 1920-1992",
        "publication_year": "1951",
        "publisher": "Gnome Press",
        "isbn": "9780553293357",
        "item_type": "Book",
        "call_number": "PS3551.S5 F6",
        "call_number_lcc": "PS3551.S5 F6",
        "call_number_dewey": "813.54",
        "summary": "The first novel in Asimov's classic science fiction masterpiece.",
    },
    {
        "biblio_id": 6,
        "title": "I, Robot",
        "author": "Asimov, Isaac, 1920-1992",
        "publication_year": "1950",
        "publisher": "Gnome Press",
        "isbn": "9780553294385",
        "item_type": "Book",
        "call_number": "PS3551.S5 I2",
        "call_number_lcc": "PS3551.S5 I2",
        "call_number_dewey": "813.54",
        "summary": "A collection of nine science fiction short stories about robots.",
    },
    {
        "biblio_id": 7,
        "title": "The Great Gatsby",
        "author": "Fitzgerald, F. Scott, 1896-1940",
        "publication_year": "1925",
        "publisher": "Charles Scribner's Sons",
        "isbn": "9780743273565",
        "item_type": "Book",
        "call_number": "PS3511.I9 G7",
        "call_number_lcc": "PS3511.I9 G7",
        "call_number_dewey": "813.52",
        "summary": "A portrait of the Jazz Age in all of its decadence and excess.",
    },
    {
        "biblio_id": 8,
        "title": "To Kill a Mockingbird",
        "author": "Lee, Harper, 1926-2016",
        "publication_year": "1960",
        "publisher": "J. B. Lippincott & Co.",
        "isbn": "9780061120084",
        "item_type": "Book",
        "call_number": "PS3562.E353 T6",
        "call_number_lcc": "PS3562.E353 T6",
        "call_number_dewey": "813.54",
        "summary": "A novel about racial injustice and the loss of innocence in the American South.",
    },
    {
        "biblio_id": 9,
        "title": "1984",
        "author": "Orwell, George, 1903-1950",
        "publication_year": "1949",
        "publisher": "Secker & Warburg",
        "isbn": "9780451524935",
        "item_type": "Book",
        "call_number": "PR6029.R8 N5",
        "call_number_lcc": "PR6029.R8 N5",
        "call_number_dewey": "823.912",
        "summary": "A dystopian novel set in a totalitarian society.",
    },
    {
        "biblio_id": 10,
        "title": "Pride and Prejudice",
        "author": "Austen, Jane, 1775-1817",
        "publication_year": "1813",
        "publisher": "T. Egerton",
        "isbn": "9780141439518",
        "item_type": "Book",
        "call_number": "PR4034 .P7",
        "call_number_lcc": "PR4034 .P7",
        "call_number_dewey": "823.7",
        "summary": "A romantic novel following the character development of Elizabeth Bennet.",
    },
    {
        "biblio_id": 11,
        "title": "The Catcher in the Rye",
        "author": "Salinger, J. D., 1919-2010",
        "publication_year": "1951",
        "publisher": "Little, Brown and Company",
        "isbn": "9780316769488",
        "item_type": "Book",
        "call_number": "PS3537.A426 C3",
        "call_number_lcc": "PS3537.A426 C3",
        "call_number_dewey": "813.54",
        "summary": "A novel about teenage alienation and loss of innocence.",
    },
    {
        "biblio_id": 12,
        "title": "One Hundred Years of Solitude",
        "author": "García Márquez, Gabriel, 1927-2014",
        "publication_year": "1967",
        "publisher": "Harper & Row",
        "isbn": "9780060883287",
        "item_type": "Book",
        "call_number": "PQ8180.17.A73 C513",
        "call_number_lcc": "PQ8180.17.A73 C513",
        "call_number_dewey": "863.64",
        "summary": "A landmark novel telling the multi-generational story of the Buendía family.",
    },
    {
        "biblio_id": 14,
        "title": "The Hobbit",
        "author": "Tolkien, J. R. R., 1892-1973",
        "publication_year": "1937",
        "publisher": "George Allen & Unwin",
        "isbn": "9780547928227",
        "item_type": "Book",
        "call_number": "PR6039.O32 H6",
        "call_number_lcc": "PR6039.O32 H6",
        "call_number_dewey": "823.912",
        "summary": "A fantasy novel about the adventures of hobbit Bilbo Baggins.",
    },
    {
        "biblio_id": 15,
        "title": "The Lord of the Rings",
        "author": "Tolkien, J. R. R., 1892-1973",
        "publication_year": "1954",
        "publisher": "George Allen & Unwin",
        "isbn": "9780618640157",
        "item_type": "Book",
        "call_number": "PR6039.O32 L6",
        "call_number_lcc": "PR6039.O32 L6",
        "call_number_dewey": "823.912",
        "summary": "An epic high-fantasy novel following the quest to destroy the One Ring.",
    },
    {
        "biblio_id": 16,
        "title": "Python Programming: An Introduction to Computer Science",
        "author": "Zelle, John M.",
        "publication_year": "2016",
        "publisher": "Franklin, Beedle & Associates",
        "isbn": "9781590282755",
        "item_type": "Book",
        "call_number": "QA76.73.P98 Z45",
        "call_number_lcc": "QA76.73.P98 Z45",
        "call_number_dewey": "005.133",
        "summary": "A textbook designed for a first course in computer science using Python.",
    },
    {
        "biblio_id": 17,
        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
        "author": "Martin, Robert C.",
        "publication_year": "2008",
        "publisher": "Prentice Hall",
        "isbn": "9780132350884",
        "item_type": "Book",
        "call_number": "QA76.76.D47 M38",
        "call_number_lcc": "QA76.76.D47 M38",
        "call_number_dewey": "005.1",
        "summary": "A guide to writing clean, readable, and maintainable code.",
    },
    {
        "biblio_id": 18,
        "title": "The Sun Also Rises",
        "author": "Hemingway, Ernest, 1899-1961",
        "publication_year": "1926",
        "publisher": "Charles Scribner's Sons",
        "isbn": "9780743297332",
        "item_type": "Book",
        "call_number": "PS3515.E37 S8",
        "call_number_lcc": "PS3515.E37 S8",
        "call_number_dewey": "813.52",
        "summary": "A novel about a group of American and British expatriates in Paris and Spain.",
    },
    {
        "biblio_id": 19,
        "title": "A Farewell to Arms",
        "author": "Hemingway, Ernest, 1899-1961",
        "publication_year": "1929",
        "publisher": "Charles Scribner's Sons",
        "isbn": "9780684801469",
        "item_type": "Book",
        "call_number": "PS3515.E37 F3",
        "call_number_lcc": "PS3515.E37 F3",
        "call_number_dewey": "813.52",
        "summary": "A novel set during World War I about an American ambulance driver and an English nurse.",
    },
    {
        "biblio_id": 20,
        "title": "The Grapes of Wrath",
        "author": "Steinbeck, John, 1902-1968",
        "publication_year": "1939",
        "publisher": "The Viking Press",
        "isbn": "9780143039433",
        "item_type": "Book",
        "call_number": "PS3537.T3234 G8",
        "call_number_lcc": "PS3537.T3234 G8",
        "call_number_dewey": "813.52",
        "summary": "A novel about the Joad family's migration from Oklahoma to California during the Dust Bowl.",
    },
]

# Sample libraries
SAMPLE_LIBRARIES = {
    "MAIN": "Main Library",
    "NORTH": "North Branch",
    "SOUTH": "South Branch",
    "CHILD": "Children's Library",
    "REF": "Reference Library",
}

# Sample locations within libraries
SAMPLE_LOCATIONS = [
    "Adult Fiction",
    "Adult Non-Fiction",
    "Young Adult",
    "Children's",
    "Reference",
    "Large Print",
    "Audio Books",
]


class MockKohaAPIClient:
    """
    Mock API client that returns sample data for testing.
    Simulates network delays for realistic behavior.
    """
    
    def __init__(self, config: KohaConfig, simulate_delay: bool = True):
        self.config = config
        self.simulate_delay = simulate_delay
        self._libraries = SAMPLE_LIBRARIES.copy()
    
    async def __aenter__(self) -> "MockKohaAPIClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        pass
    
    async def _delay(self, min_ms: int = 100, max_ms: int = 500) -> None:
        """Simulate network delay."""
        if self.simulate_delay:
            delay = random.randint(min_ms, max_ms) / 1000
            await asyncio.sleep(delay)
    
    async def search_biblios(
        self,
        query: str,
        search_type: str = "title",
        page: int = 1,
        per_page: int = 10,
    ) -> Tuple[Optional[SearchResult], Optional[str]]:
        """Search for bibliographic records using sample data."""
        await self._delay()
        
        query_lower = query.lower()
        
        # Filter books based on search type
        matches = []
        for book in SAMPLE_BOOKS:
            if search_type == "title" or search_type == "title_exact":
                if query_lower in book["title"].lower():
                    matches.append(book)
            elif search_type == "author":
                if query_lower in book["author"].lower():
                    matches.append(book)
            elif search_type == "isbn":
                if query_lower.replace("-", "") in book["isbn"].replace("-", ""):
                    matches.append(book)
            elif search_type == "subject" or search_type == "keyword":
                # Search in title, author, and summary
                searchable = f"{book['title']} {book['author']} {book.get('summary', '')}".lower()
                if query_lower in searchable:
                    matches.append(book)
            else:
                # Default: search title
                if query_lower in book["title"].lower():
                    matches.append(book)
        
        # Paginate results
        total = len(matches)
        start = (page - 1) * per_page
        end = start + per_page
        page_matches = matches[start:end]
        
        # Convert to BiblioRecord objects
        records = []
        for book in page_matches:
            records.append(BiblioRecord(
                biblio_id=book["biblio_id"],
                title=book["title"],
                author=book["author"],
                publication_year=book["publication_year"],
                publisher=book["publisher"],
                isbn=book["isbn"],
                item_type=book["item_type"],
                call_number=book["call_number"],
                call_number_lcc=book.get("call_number_lcc", ""),
                call_number_dewey=book.get("call_number_dewey", ""),
                summary=book.get("summary", ""),
                raw_data=book,
            ))
        
        return SearchResult(records, total, page, per_page), None
    
    async def get_biblio(self, biblio_id: int) -> Tuple[Optional[BiblioRecord], Optional[str]]:
        """Get a single bibliographic record by ID."""
        await self._delay()
        
        for book in SAMPLE_BOOKS:
            if book["biblio_id"] == biblio_id:
                return BiblioRecord(
                    biblio_id=book["biblio_id"],
                    title=book["title"],
                    author=book["author"],
                    publication_year=book["publication_year"],
                    publisher=book["publisher"],
                    isbn=book["isbn"],
                    item_type=book["item_type"],
                    call_number=book["call_number"],
                    call_number_lcc=book.get("call_number_lcc", ""),
                    call_number_dewey=book.get("call_number_dewey", ""),
                    summary=book.get("summary", ""),
                    raw_data=book,
                ), None
        
        return None, "Record not found"
    
    async def get_biblio_items(self, biblio_id: int) -> Tuple[List[HoldingItem], Optional[str]]:
        """Get items (holdings) for a bibliographic record."""
        await self._delay()
        
        # Check if biblio exists
        book = None
        for b in SAMPLE_BOOKS:
            if b["biblio_id"] == biblio_id:
                book = b
                break
        
        if not book:
            return [], "Record not found"
        
        # Generate random holdings
        holdings = []
        num_copies = random.randint(1, 5)
        
        library_ids = list(SAMPLE_LIBRARIES.keys())
        
        for i in range(num_copies):
            library_id = random.choice(library_ids)
            location = random.choice(SAMPLE_LOCATIONS)
            
            # Randomly determine availability
            is_available = random.random() > 0.3  # 70% chance available
            
            if is_available:
                status = "Available"
                due_date = None
            else:
                status = "On Loan"
                # Generate a random due date
                import datetime
                days_until_due = random.randint(1, 21)
                due = datetime.date.today() + datetime.timedelta(days=days_until_due)
                due_date = due.strftime("%Y-%m-%d")
            
            # Generate a random public note occasionally
            public_note = ""
            if random.random() > 0.7:  # 30% chance of having a note
                notes = [
                    "Signed by author",
                    "Large print edition",
                    "Includes supplementary materials",
                    "Replacement copy",
                    "Gift from Friends of the Library",
                ]
                public_note = random.choice(notes)
            
            holdings.append(HoldingItem(
                item_id=biblio_id * 100 + i + 1,
                barcode=f"{biblio_id:06d}{i+1:03d}",
                library_id=library_id,
                library_name=SAMPLE_LIBRARIES[library_id],
                location=location,
                call_number=book["call_number"],
                copy_number=i + 1,
                status=status,
                is_available=is_available,
                due_date=due_date,
                item_type=book["item_type"],
                notes=public_note,
                public_note=public_note,
            ))
        
        return holdings, None
    
    async def get_libraries(self) -> Tuple[Dict[str, str], Optional[str]]:
        """Get list of libraries."""
        await self._delay(50, 100)
        return self._libraries, None
