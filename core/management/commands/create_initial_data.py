# your_app/management/commands/create_initial_data.py

from django.core.management.base import BaseCommand
from core.models import Employee, Outlet
from menu.models import MenuItemCategory, MenuItem, MenuItemVariation
from orders.models import Table
from faker import Faker


class Command(BaseCommand):
    help = 'Creates initial data for the application'

    def handle(self, *args, **options):
        fake = Faker()

        # Create outlet
        outlet = Outlet.objects.create(
            name=fake.company(),
            manager=fake.name(),
            address=fake.address(),
            contact_info=fake.phone_number()
        )

       # Create employees
        for _ in range(10):
            e = Employee.objects.create(
                department=fake.job(),
                outlet=outlet,
                username=fake.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                contact_info=fake.phone_number(),
                # Adjust the chance of being admin as needed
                is_admin=fake.boolean(chance_of_getting_true=20),

            )
            e.set_password("123")
            e.save()

       # Create item categories
        for _ in range(10):
            MenuItemCategory.objects.create(
                outlet=outlet,
                name=fake.word()
            )

        # Create menu items
        for category in MenuItemCategory.objects.all():
            for _ in range(10):
                MenuItem.objects.create(
                    category=category,
                    name=fake.word(),
                    short_code=fake.word(),
                    description=fake.sentence(),
                    price=fake.random_number(digits=2),
                    tax=fake.random_number(digits=1),
                    veg=fake.boolean(),
                    available=fake.boolean()
                )

        # Create variations of the items
        for item in MenuItem.objects.all():
            for _ in range(3):
                MenuItemVariation.objects.create(
                    menu_item=item,
                    name=fake.word(),
                    price_variation=fake.random_number(digits=2)
                )

        # Create tables
        for _ in range(10):
            Table.objects.create(
                outlet=outlet,
                name=fake.word(),
            )
        self.stdout.write(self.style.SUCCESS(
            'Initial data created successfully'))
