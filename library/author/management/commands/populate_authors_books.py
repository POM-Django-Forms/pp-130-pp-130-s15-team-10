import datetime

from django.core.management.base import BaseCommand
from book.models import Book
from author.models import Author
import random
from django.db.utils import IntegrityError
from datetime import date


class Command(BaseCommand):
    help = "Populate authors and books into the database"

    def handle(self, *args, **options):
        books_data = [
            ("Little Women", "Louisa", "May", "Alcott", 2023, None),
            ("Emma", "Jane", "", "Austen", 2020, None),
            ("Pride and Prejudice", "Jane", "", "Austen", 2023, date(2024, 7, 9)),
            ("Mansfield Park", "Jane", "", "Austen", 2024, date(2024, 5, 25)),
            ("Persuasion", "Jane", "", "Austen", 2024, None),
            ("Sense and Sensibility", "Jane", "", "Austen", 2022, date(2024, 2, 13)),
            ("Lorna Doone", "R.D.", "", "Blackmore", 2023, None),
            ("The Tenant of Wildfell Hall", "Anne", "", "Bronte", 2021, date(2024, 11, 2)),
            ("Jane Eyre", "Charlotte", "", "Bronte", 2020, None),
            ("The Professor", "Charlotte", "", "Bronte", 2023, None),
            ("Shirley", "Charlotte", "", "Bronte", 2024, None),
            ("Villette", "Charlotte", "", "Bronte", 2023, date(2024, 5, 5)),
            ("Wuthering Heights", "Emily", "", "Bronte", 2020, None),
            ("The Pilgrim's Progress", "John", "", "Bunyan", 2022, None),
            ("Little Lord Fauntleroy", "Frances", "Hodgson", "Burnett", 2021, None),
            ("The Secret Garden", "Frances", "Hodgson", "Burnett", 2021, date(2024, 8, 18)),
            ("Alice's Adventures in Wonderland", "Lewis", "", "Carroll", 2022, None),
            ("Through the Looking-Glass", "Lewis", "", "Carroll", 2021, None),
            ("The Moonstone", "Wilkie", "", "Collins", 2023, None),
            ("The Woman in White", "Wilkie", "", "Collins", 2022, date(2024, 1, 30)),
            ("The Adventures of Pinocchio", "Carlo", "", "Collodi", 2020, None),
            ("Lord Jim", "Joseph", "", "Conrad", 2020, None),
            ("What Katy Did", "Susan", "", "Coolidge", 2021, None),
            ("The Last of the Mohicans", "James", "Fenimore", "Cooper", 2023, date(2024, 3, 14)),
            ("Robinson Crusoe", "Daniel", "", "Defoe", 2023, None),
            ("Barnaby Rudge", "Charles", "", "Dickens", 2024, None),
            ("Bleak House", "Charles", "", "Dickens", 2022, None),
            ("A Christmas Carol", "Charles", "", "Dickens", 2024, date(2024, 9, 12)),
            ("David Copperfield", "Charles", "", "Dickens", 2023, None),
            ("Dombey and Son", "Charles", "", "Dickens", 2020, None),
            ("Great Expectations", "Charles", "", "Dickens", 2022, None),
            ("Hard Times", "Charles", "", "Dickens", 2021, None),
            ("Martin Chuzzlewit", "Charles", "", "Dickens", 2024, date(2024, 4, 20)),
            ("Nicholas Nickleby", "Charles", "", "Dickens", 2023, None),
            ("The Old Curiosity Shop", "Charles", "", "Dickens", 2020, None),
            ("Oliver Twist", "Charles", "", "Dickens", 2021, None),
            ("The Pickwick Papers", "Charles", "", "Dickens", 2023, None),
            ("A Tale of Two Cities", "Charles", "", "Dickens", 2023, date(2024, 7, 7)),
            ("The Adventures of Sherlock Holmes", "Arthur", "", "Conan Doyle", 2024, None),
            ("The Case-Book of Sherlock Holmes", "Arthur", "", "Conan Doyle", 2022, None),
            ("The Count of Monte Cristo", "Alexandre", "", "Dumas", 2023, None),
            ("The Three Musketeers", "Alexandre", "", "Dumas", 2020, date(2024, 8, 30)),
            ("Adam Bede", "George", "", "Eliot", 2023, None),
            ("Middlemarch", "George", "", "Eliot", 2021, None),
            ("The Mill on the Floss", "George", "", "Eliot", 2020, None),
            ("King Solomon's Mines", "H.", "Rider", "Haggard", 2024, None),
            ("Far from the Madding Crowd", "Thomas", "", "Hardy", 2023, None),
            ("The Mayor of Casterbridge", "Thomas", "", "Hardy", 2022, None),
            ("Tess of the d'Urbervilles", "Thomas", "", "Hardy", 2021, date(2024, 3, 1)),
            ("Under the Greenwood Tree", "Thomas", "", "Hardy", 2024, None),
            ("The Scarlet Letter", "Nathaniel", "", "Hawthorne", 2023, None),
            ("The Hunchback of Notre-Dame", "Victor", "", "Hugo", 2023, None),
            ("Les Miserables", "Victor", "", "Hugo", 2021, date(2024, 6, 15)),
            ("The Sketch Book of Geoffrey Crayon, Gent.", "Washington", "", "Irving", 2022, None),
            ("Westward Ho!", "Charles", "", "Kingsley", 2024, None),
            ("Sons and Lovers", "D.H.", "", "Lawrence", 2020, None),
            ("The Phantom of the Opera", "Gaston", "", "Leroux", 2021, None),
            ("The Call of the Wild", "Jack", "", "London", 2023, None),
            ("White Fang", "Jack", "", "London", 2022, date(2024, 2, 28)),
            ("Moby-Dick", "Herman", "", "Melville", 2024, None),
            ("Tales of Mystery & Imagination", "Edgar", "Allan", "Poe", 2021, None),
            ("Ivanhoe", "Walter", "", "Scott", 2023, None),
            ("Rob Roy", "Walter", "", "Scott", 2020, None),
            ("Waverley", "Walter", "", "Scott", 2022, date(2024, 1, 10)),
            ("Black Beauty", "Anna", "", "Sewell", 2024, None),
            ("All's Well That Ends Well", "William", "", "Shakespeare", 2023, None),
            ("Antony and Cleopatra", "William", "", "Shakespeare", 2022, None),
            ("As You Like It", "William", "", "Shakespeare", 2021, None),
            ("The Comedy of Errors", "William", "", "Shakespeare", 2020, None),
            ("Hamlet", "William", "", "Shakespeare", 2023, date(2024, 4, 5)),
            ("Henry V", "William", "", "Shakespeare", 2023, None),
            ("Julius Caesar", "William", "", "Shakespeare", 2022, None),
            ("King Lear", "William", "", "Shakespeare", 2024, None),
            ("Love's Labour's Lost", "William", "", "Shakespeare", 2021, None),
            ("Macbeth", "William", "", "Shakespeare", 2020, None),
            ("The Merchant of Venice", "William", "", "Shakespeare", 2022, None),
            ("A Midsummer Night's Dream", "William", "", "Shakespeare", 2023, None),
            ("Much Ado About Nothing", "William", "", "Shakespeare", 2023, None),
            ("Othello", "William", "", "Shakespeare", 2020, None),
            ("Richard III", "William", "", "Shakespeare", 2021, None),
            ("Romeo and Juliet", "William", "", "Shakespeare", 2024, None),
            ("The Taming of the Shrew", "William", "", "Shakespeare", 2024, date(2024, 5, 15)),
            ("The Tempest", "William", "", "Shakespeare", 2022, None),
            ("Timon of Athens", "William", "", "Shakespeare", 2020, None),
            ("Titus Andronicus", "William", "", "Shakespeare", 2023, None),
            ("Twelfth Night", "William", "", "Shakespeare", 2021, None),
            ("The Winter's Tale", "William", "", "Shakespeare", 2023, None),
            ("Kidnapped", "Robert", "Louis", "Stevenson", 2022, None),
            ("Strange Case of Dr Jekyll and Mr Hyde", "Robert", "Louis", "Stevenson", 2024, None),
            ("Treasure Island", "Robert", "Louis", "Stevenson", 2023, date(2024, 3, 30)),
            ("Uncle Tom's Cabin", "Harriet", "Beecher", "Stowe", 2023, None),
            ("Gulliver's Travels", "Jonathan", "", "Swift", 2021, None),
            ("Vanity Fair", "William", "Makepeace", "Thackeray", 2024, None),
            ("Barchester Towers", "Anthony", "", "Trollope", 2020, None),
            ("Adventures of Huckleberry Finn", "Mark", "", "Twain", 2022, None),
            ("The Adventures of Tom Sawyer", "Mark", "", "Twain", 2021, None),
            ("Around the World in Eighty Days", "Jules", "", "Verne", 2023, None),
            ("20,000 Leagues Under the Sea", "Jules", "", "Verne", 2024, date(2024, 7, 20)),
            ("The Importance of Being Earnest", "Oscar", "", "Wilde", 2023, None),
            ("The Picture of Dorian Gray", "Oscar", "", "Wilde", 2022, None)
        ]

        for title, first, middle, last, year, issue_date in books_data:
            author, _ = Author.objects.get_or_create(
                name=first,
                surname=last,
                patronymic=middle if middle else ""
            )
            try:
                book, created = Book.objects.get_or_create(
                    name=title,
                    defaults={
                        'description': f"{title} by {first} {last}",
                        'count': random.randint(1, 10),
                        'publication_year': year,
                        'date_of_issue': (
                            issue_date if isinstance(issue_date, date) else
                            datetime.strptime(issue_date, "%Y-%m-%d").date() if issue_date else None
                        )
                    }
                )
                book.authors.add(author)
            except IntegrityError:
                self.stdout.write(self.style.WARNING(f"Skipped duplicate book: {title}"))

        self.stdout.write(self.style.SUCCESS("Data populated."))
