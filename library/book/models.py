from django.db import models


class Book(models.Model):
    """
        This class represents an Author. \n
        Attributes:
        -----------
        param name: Describes name of the book
        type name: str max_length=128
        param description: Describes description of the book
        type description: str
        param count: Describes count of the book
        type count: int default=10
        param authors: list of Authors
        type authors: list->Author
    """
    name = models.CharField(unique=True, max_length=128)
    description = models.CharField(blank=True, max_length=256)
    count = models.IntegerField(default=10)
    publication_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="Year of Publication")
    source_url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Source URL",
        help_text="Source URL about the book"
    )
    date_of_issue = models.DateField(blank=True, null=True, verbose_name="Date of Issue")

    def __str__(self):
        """
        Magic method is redefined to show all information about Book.
        :return: book id, book name, book description, book count, book authors
        """
        return (
            f"'id': {self.id}, "
            f"'name': '{self.name}', "
            f"'description': '{self.description}', "
            f"'count': {self.count}, "
            f"'publication_year': {self.publication_year}, "
            f"'authors': [{', '.join(author.name + ' ' + author.surname for author in self.authors.all())}]"
        )

    def __repr__(self):
        """
        This magic method is redefined to show class and id of Book object.
        :return: class, id
        """
        return f"Book(id={self.id})"

    @staticmethod
    def get_by_id(book_id):
        """
        :param book_id: SERIAL: the id of a Book to be found in the DB
        :return: book object or None if a book with such ID does not exist
        """
        return Book.objects.filter(id=book_id).first()

    @staticmethod
    def delete_by_id(book_id):
        """
        :param book_id: an id of a book to be deleted
        :type book_id: int
        :return: True if object existed in the db and was removed or False if it didn't exist
        """
        if Book.get_by_id(book_id) is None:
            return False
        Book.objects.get(id=book_id).delete()
        return True

    @staticmethod
    def create(name, description, count=10, authors=None, publication_year=None, date_of_issue=None):
        """
        param name: Describes name of the book
        type name: str max_length=128
        param description: Describes description of the book
        type description: str
        param count: Describes count of the book
        type count: int default=10
        param authors: list of Authors
        type authors: list->Author
        :return: a new book object which is also written into the DB
        """
        if len(name) > 128:
            return None

        book = Book(
            name=name,
            description=description,
            count=count,
            publication_year=publication_year,
            date_of_issue=date_of_issue
        )
        book.save()
        if authors is not None:
            book.authors.set(authors)
        return book

    def to_dict(self):
        """
        :return: book id, book name, book description, book count, book authors
        :Example:
        | {
        |   'id': 8,
        |   'name': 'django book',
        |   'description': 'bla bla bla',
        |   'count': 10',
        |   'authors': []
        | }
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'count': self.count,
            'publication_year': self.publication_year,
            'date_of_issue': str(self.date_of_issue) if self.date_of_issue else None,
            'authors': [author.id for author in self.authors.all()]
        }

    def update(self, name=None, description=None, count=None, publication_year=None, date_of_issue=None):
        """
        Updates book in the database with the specified parameters.\n
        param name: Describes name of the book
        type name: str max_length=128
        param description: Describes description of the book
        type description: str
        param count: Describes count of the book
        type count: int default=10
        :return: None
        """
        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        if count is not None:
            self.count = count

        if publication_year is not None:
            self.publication_year = publication_year

        if date_of_issue is not None:
            self.date_of_issue = date_of_issue

        self.save()

    def add_authors(self, authors):
        """
        Add  authors to  book in the database with the specified parameters.\n
        param authors: list authors
        :return: None
        """
        if (authors is not None):
            for elem in authors:
                self.authors.add(elem)
                self.save()

    def remove_authors(self, authors):
        """
        Remove authors to  book in the database with the specified parameters.\n
        param authors: list authors
        :return: None
        """
        if authors:
            for author in authors:
                self.authors.remove(author)

    @staticmethod
    def get_all(cls):
        """
        returns data for json request with QuerySet of all book
        """
        return cls.objects.all().prefetch_related('authors').distinct()

    def update_limited_fields(self, date_of_issue=None, count=None, book_source_url=None):
        """
        Update 3 fields.

        :param date_of_issue: datetime.date або None
        :param count: int або None
        :param book_source_url: str або None
        :return: None
        """
        if date_of_issue is not None:
            self.date_of_issue = date_of_issue

        if count is not None:
            self.count = count

        if book_source_url is not None:
            self.book_source_url = book_source_url

        self.save()
