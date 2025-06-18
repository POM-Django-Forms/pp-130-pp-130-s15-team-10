from django.core.management.base import BaseCommand
from book.models import Book
from author.models import Author
import random
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = "Populate authors and books into the database"

    def handle(self, *args, **options):
        books_data = [
            ("Little Women", "Louisa", "May", "Alcott"),
            ("Emma", "Jane", "", "Austen"),
            ("Pride and Prejudice", "Jane", "", "Austen"),
            ("Mansfield Park", "Jane", "", "Austen"),
            ("Persuasion", "Jane", "", "Austen"),
            ("Sense and Sensibility", "Jane", "", "Austen"),
            ("Lorna Doone", "R.D.", "", "Blackmore"),
            ("The Tenant of Wildfell Hall", "Anne", "", "Bronte"),
            ("Jane Eyre", "Charlotte", "", "Bronte"),
            ("The Professor", "Charlotte", "", "Bronte"),
            ("Shirley", "Charlotte", "", "Bronte"),
            ("Villette", "Charlotte", "", "Bronte"),
            ("Wuthering Heights", "Emily", "", "Bronte"),
            ("The Pilgrim's Progress", "John", "", "Bunyan"),
            ("Little Lord Fauntleroy", "Frances", "Hodgson", "Burnett"),
            ("The Secret Garden", "Frances", "Hodgson", "Burnett"),
            ("Alice's Adventures in Wonderland", "Lewis", "", "Carroll"),
            ("Through the Looking-Glass", "Lewis", "", "Carroll"),
            ("The Moonstone", "Wilkie", "", "Collins"),
            ("The Woman in White", "Wilkie", "", "Collins"),
            ("The Adventures of Pinocchio", "Carlo", "", "Collodi"),
            ("Lord Jim", "Joseph", "", "Conrad"),
            ("What Katy Did", "Susan", "", "Coolidge"),
            ("The Last of the Mohicans", "James", "Fenimore", "Cooper"),
            ("Robinson Crusoe", "Daniel", "", "Defoe"),
            ("Barnaby Rudge", "Charles", "", "Dickens"),
            ("Bleak House", "Charles", "", "Dickens"),
            ("A Christmas Carol", "Charles", "", "Dickens"),
            ("David Copperfield", "Charles", "", "Dickens"),
            ("Dombey and Son", "Charles", "", "Dickens"),
            ("Great Expectations", "Charles", "", "Dickens"),
            ("Hard Times", "Charles", "", "Dickens"),
            ("Martin Chuzzlewit", "Charles", "", "Dickens"),
            ("Nicholas Nickleby", "Charles", "", "Dickens"),
            ("The Old Curiosity Shop", "Charles", "", "Dickens"),
            ("Oliver Twist", "Charles", "", "Dickens"),
            ("The Pickwick Papers", "Charles", "", "Dickens"),
            ("A Tale of Two Cities", "Charles", "", "Dickens"),
            ("The Adventures of Sherlock Holmes", "Arthur", "", "Conan Doyle"),
            ("The Case-Book of Sherlock Holmes", "Arthur", "", "Conan Doyle"),
            ("The Count of Monte Cristo", "Alexandre", "", "Dumas"),
            ("The Three Musketeers", "Alexandre", "", "Dumas"),
            ("Adam Bede", "George", "", "Eliot"),
            ("Middlemarch", "George", "", "Eliot"),
            ("The Mill on the Floss", "George", "", "Eliot"),
            ("King Solomon's Mines", "H.", "Rider", "Haggard"),
            ("Far from the Madding Crowd", "Thomas", "", "Hardy"),
            ("The Mayor of Casterbridge", "Thomas", "", "Hardy"),
            ("Tess of the d'Urbervilles", "Thomas", "", "Hardy"),
            ("Under the Greenwood Tree", "Thomas", "", "Hardy"),
            ("The Scarlet Letter", "Nathaniel", "", "Hawthorne"),
            ("The Hunchback of Notre-Dame", "Victor", "", "Hugo"),
            ("Les Miserables", "Victor", "", "Hugo"),
            ("The Sketch Book of Geoffrey Crayon, Gent.", "Washington", "", "Irving"),
            ("Westward Ho!", "Charles", "", "Kingsley"),
            ("Sons and Lovers", "D.H.", "", "Lawrence"),
            ("The Phantom of the Opera", "Gaston", "", "Leroux"),
            ("The Call of the Wild", "Jack", "", "London"),
            ("White Fang", "Jack", "", "London"),
            ("Moby-Dick", "Herman", "", "Melville"),
            ("Tales of Mystery & Imagination", "Edgar", "Allan", "Poe"),
            ("Ivanhoe", "Walter", "", "Scott"),
            ("Rob Roy", "Walter", "", "Scott"),
            ("Waverley", "Walter", "", "Scott"),
            ("Black Beauty", "Anna", "", "Sewell"),
            ("All's Well That Ends Well", "William", "", "Shakespeare"),
            ("Antony and Cleopatra", "William", "", "Shakespeare"),
            ("As You Like It", "William", "", "Shakespeare"),
            ("The Comedy of Errors", "William", "", "Shakespeare"),
            ("Hamlet", "William", "", "Shakespeare"),
            ("Henry V", "William", "", "Shakespeare"),
            ("Julius Caesar", "William", "", "Shakespeare"),
            ("King Lear", "William", "", "Shakespeare"),
            ("Love's Labour's Lost", "William", "", "Shakespeare"),
            ("Macbeth", "William", "", "Shakespeare"),
            ("The Merchant of Venice", "William", "", "Shakespeare"),
            ("A Midsummer Night's Dream", "William", "", "Shakespeare"),
            ("Much Ado About Nothing", "William", "", "Shakespeare"),
            ("Othello", "William", "", "Shakespeare"),
            ("Richard III", "William", "", "Shakespeare"),
            ("Romeo and Juliet", "William", "", "Shakespeare"),
            ("The Taming of the Shrew", "William", "", "Shakespeare"),
            ("The Tempest", "William", "", "Shakespeare"),
            ("Timon of Athens", "William", "", "Shakespeare"),
            ("Titus Andronicus", "William", "", "Shakespeare"),
            ("Twelfth Night", "William", "", "Shakespeare"),
            ("The Winter's Tale", "William", "", "Shakespeare"),
            ("Kidnapped", "Robert", "Louis", "Stevenson"),
            ("Strange Case of Dr Jekyll and Mr Hyde", "Robert", "Louis", "Stevenson"),
            ("Treasure Island", "Robert", "Louis", "Stevenson"),
            ("Uncle Tom's Cabin", "Harriet", "Beecher", "Stowe"),
            ("Gulliver's Travels", "Jonathan", "", "Swift"),
            ("Vanity Fair", "William", "Makepeace", "Thackeray"),
            ("Barchester Towers", "Anthony", "", "Trollope"),
            ("Adventures of Huckleberry Finn", "Mark", "", "Twain"),
            ("The Adventures of Tom Sawyer", "Mark", "", "Twain"),
            ("Around the World in Eighty Days", "Jules", "", "Verne"),
            ("20,000 Leagues Under the Sea", "Jules", "", "Verne"),
            ("The Importance of Being Earnest", "Oscar", "", "Wilde"),
            ("The Picture of Dorian Gray", "Oscar", "", "Wilde"),
        ]

        for title, first, middle, last in books_data:
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
                    }
                )
                book.authors.add(author)
            except IntegrityError:
                self.stdout.write(self.style.WARNING(f"Skipped duplicate book: {title}"))

        self.stdout.write(self.style.SUCCESS("Data populated."))
