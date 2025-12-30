"""
Timetable app models
"""
from django.db import models


class Cohort(models.Model):
    """
    Represents a student cohort/batch
    Example: BAPM_2023, BCS_2024
    """
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Cohorts'
    
    def __str__(self):
        return self.name


class Section(models.Model):
    """
    Represents a section within a cohort
    Example: Section A, Section B
    """
    name = models.CharField(max_length=100)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='sections')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'cohort']
        ordering = ['cohort', 'name']
    
    def __str__(self):
        return f"{self.cohort.name} - {self.name}"


class Instructor(models.Model):
    """
    Represents an instructor/lecturer
    """
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Represents a course
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class TimetableEntry(models.Model):
    """
    Represents a scheduled session in the timetable
    """
    SESSION_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    TYPE_CHOICES = [
        ('Lecture', 'Lecture'),
        ('Lab', 'Lab'),
        ('Tutorial', 'Tutorial'),
        ('Office Hours', 'Office Hours'),
        ('Practical', 'Practical'),
    ]
    
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='timetable_entries')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetable_entries')
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='timetable_entries')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='timetable_entries')
    
    session = models.CharField(max_length=20, choices=SESSION_CHOICES)
    time_interval = models.CharField(max_length=100)  # e.g., "9:00-10:00"
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Lecture')
    classroom = models.CharField(max_length=255, default='N/A')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['cohort', 'section', 'session']
        verbose_name_plural = 'Timetable Entries'
        unique_together = ['cohort', 'section', 'instructor', 'session', 'time_interval']
    
    def __str__(self):
        return f"{self.cohort.name} - {self.session} - {self.time_interval}"
