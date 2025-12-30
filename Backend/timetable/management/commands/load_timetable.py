"""
Django management command to load timetable data from JSON file
Usage: python manage.py load_timetable
"""
import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from timetable.models import Cohort, Section, Instructor, Course, TimetableEntry


class Command(BaseCommand):
    help = 'Load timetable data from JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            help='Path to JSON file to load',
            default=None
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing timetable data before loading',
        )

    def handle(self, *args, **options):
        # Get JSON file path
        json_file = options.get('json_file')
        
        if not json_file:
            # Try default locations
            json_file = os.path.join(settings.BASE_DIR, '../Frontend/data/timetable.json')
            if not os.path.exists(json_file):
                json_file = os.path.join(settings.BASE_DIR, 'timetable.json')
        
        if not os.path.exists(json_file):
            raise CommandError(f'JSON file not found: {json_file}')
        
        # Clear existing data if requested
        if options.get('clear'):
            self.stdout.write(self.style.WARNING('Clearing existing timetable data...'))
            TimetableEntry.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Timetable data cleared'))
        
        # Load JSON
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise CommandError(f'Error loading JSON file: {str(e)}')
        
        # Parse and load data
        total_entries = 0
        
        for term, sections in data.items():
            self.stdout.write(f'Processing term: {term}')
            
            for section_name, days in sections.items():
                # Extract cohort and section info
                parts = section_name.split('_Section_')
                if len(parts) != 2:
                    self.stdout.write(self.style.WARNING(f'  Skipping invalid section name: {section_name}'))
                    continue
                
                cohort_name = parts[0]
                section_letter = parts[1]
                
                # Get or create cohort
                cohort, _ = Cohort.objects.get_or_create(name=cohort_name)
                
                # Get or create section
                section, _ = Section.objects.get_or_create(
                    name=section_letter,
                    cohort=cohort
                )
                
                # Process sessions
                for day, sessions in days.items():
                    for session_key, session_data in sessions.items():
                        try:
                            course_name = session_data.get('Course', 'Unknown')
                            instructor_name = session_data.get('Instructor', 'Unknown')
                            time_interval = session_data.get('Time', '00:00-00:00')
                            session_type = session_data.get('Type', 'Lecture')
                            classroom = session_data.get('Classroom', 'N/A')
                            
                            # Get or create instructor
                            instructor, _ = Instructor.objects.get_or_create(
                                name=instructor_name
                            )
                            
                            # Get or create course
                            course_code = self._extract_course_code(course_name)
                            course, _ = Course.objects.get_or_create(
                                code=course_code,
                                defaults={'name': course_name}
                            )
                            
                            # Create timetable entry
                            entry, created = TimetableEntry.objects.get_or_create(
                                cohort=cohort,
                                section=section,
                                instructor=instructor,
                                course=course,
                                session=day,
                                time_interval=time_interval,
                                defaults={
                                    'type': session_type,
                                    'classroom': classroom
                                }
                            )
                            
                            if created:
                                total_entries += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'  [+] Created: {cohort_name} {section_letter} - '
                                        f'{day} {time_interval} - {course_name}'
                                    )
                                )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'  [-] Error processing session: {str(e)}'
                                )
                            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully loaded {total_entries} timetable entries!'
            )
        )
    
    def _extract_course_code(self, course_name):
        """Extract a course code from course name"""
        # Create a simple code from the first letters of each word
        words = course_name.split()
        code = ''.join([word[0].upper() for word in words if word])
        return code[:20] if code else 'UNKNOWN'
