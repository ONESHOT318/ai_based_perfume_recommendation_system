import csv
import os

from django.core.management.base import BaseCommand
from ai_perfume_recommender.models import Perfume, Note


class Command(BaseCommand):
    help = "Import perfumes from CSV file"

    def handle(self, *args, **kwargs):

        # 📁 CSV yolu
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        csv_path = os.path.join(base_dir, "data", "perfume.csv")

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:

                perfume, created = Perfume.objects.get_or_create(
                    name=row["name"].strip(),
                    brand=row["brand"].strip(),
                    defaults={
                        "category": row["category"].strip(),
                        "gender": row["gender"].strip().lower(),
                        "season": row["season"].strip(),
                        "longevity": row["longevity"].strip(),
                    }
                )

                # 🔥 notaları parçala
                notes_text = row["notes"]

                note_names = [
                    n.strip().lower()
                    for n in notes_text.replace(";", ",").split(",")
                    if n.strip()
                ]

                for note_name in note_names:
                    note, _ = Note.objects.get_or_create(name=note_name)
                    perfume.notes.add(note)

        self.stdout.write(self.style.SUCCESS("Perfumes imported successfully!"))