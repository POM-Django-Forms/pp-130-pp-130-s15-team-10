from django.core.management.base import BaseCommand
from authentication.models import CustomUser
from order.models import Order
from book.models import Book
from django.utils import timezone
import random
from datetime import timedelta


class Command(BaseCommand):
    help = "Populate the database with users and orders"

    FIRST_NAMES = [
        "Olena", "Ihor", "Sofiia", "Andrii", "Kateryna",
        "Dmytro", "Anastasiia", "Oleh", "Natalia", "Taras",
        "Yuliia", "Serhii", "Viktoriia", "Bohdan", "Inna",
        "Artem", "Mariia", "Yevhen", "Alina", "Roman"
    ]

    LAST_NAMES = [
        "Shevchenko", "Kovalenko", "Tkachenko", "Bondarenko", "Kravchenko",
        "Boyko", "Kovalchuk", "Melnyk", "Marchenko", "Rudenko",
        "Hrytsenko", "Moroz", "Savchenko", "Lysenko", "Polishchuk",
        "Tymoshenko", "Mazur", "Pavlenko", "Voronov", "Shapoval"
    ]

    MIDDLE_NAMES = [
        "Oleksandrivna", "Petrovych", "Volodymyrivna", "Ivanovych",
        "Sergiivna", "Mykolayovych", "Yuriyivna", "Olegovych",
        "Vasylivna", "Andriyovych", "Oleksiyivna", "Stepanovych",
        "Leonidivna", "Maksymovych", "Borysivna", "Denysovych",
        "Hryhorivna", "Valeriyovych", "Vitaliivna", "Tarasovych"
    ]

    def handle(self, *args, **options):
        for i in range(20):
            role = 1 if i == 0 else 0
            email = f"user{i + 1}@example.com"

            first = self.FIRST_NAMES[i % len(self.FIRST_NAMES)]
            last = self.LAST_NAMES[i % len(self.LAST_NAMES)]
            middle = self.MIDDLE_NAMES[i % len(self.MIDDLE_NAMES)]

            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'middle_name': middle,
                    'is_active': True,
                    'is_staff': role == 1,
                    'role': role
                }
            )
            if created:
                user.set_password("password123")
                user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {first} {middle} {last}"))

            books = list(Book.objects.all())
            random.shuffle(books)
            order_count = random.randint(2, 4)
            created_orders = 0

            for book in books:
                if created_orders >= order_count:
                    break

                existing = Order.objects.filter(user=user, book=book, end_at__isnull=True).exists()
                taken = Order.objects.filter(book=book, end_at__isnull=True).count()

                if not existing and taken < (book.count - 1):
                    created_at = timezone.now()
                    plated_end_at = created_at + timedelta(days=14)

                    order = Order.create(
                        user=user,
                        book=book,
                        plated_end_at=plated_end_at
                    )

                    if order:
                        created_orders += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"  -> Order: {book.name} for {first} {last}"
                        ))

        self.stdout.write(self.style.SUCCESS("Users and orders populated successfully."))
