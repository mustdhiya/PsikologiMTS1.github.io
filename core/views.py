from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from students.models import Student, StudentAchievement
from testsystem.models import RMIBScore, RMIBCategory
import json

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic Statistics
        total_students = Student.objects.count()
        completed_tests = RMIBScore.objects.filter(is_completed=True).count()
        pending_tests = Student.objects.filter(test_status='pending').count()
        in_progress_tests = Student.objects.filter(test_status='in_progress').count()
        
        # Calculate completion rate
        completion_rate = round((completed_tests / total_students * 100) if total_students > 0 else 0, 1)
        
        # Average score calculation (you can customize this based on your scoring logic)
        avg_scores = RMIBScore.objects.filter(is_completed=True).aggregate(
            avg_outdoor=Avg('outdoor'),
            avg_mechanical=Avg('mechanical'),
            avg_computational=Avg('computational'),
            avg_scientific=Avg('scientific'),
            avg_personal=Avg('personal'),
            avg_aesthetic=Avg('aesthetic'),
            avg_literary=Avg('literary'),
            avg_musical=Avg('musical'),
            avg_social_service=Avg('social_service'),
            avg_clerical=Avg('clerical'),
            avg_practical=Avg('practical'),
            avg_medical=Avg('medical'),
        )
        
        # Calculate overall average
        individual_avgs = [v for v in avg_scores.values() if v is not None]
        overall_average = round(sum(individual_avgs) / len(individual_avgs) if individual_avgs else 0, 1)
        
        # Interest distribution for chart
        interest_distribution = self.get_interest_distribution()
        
        # Class performance data
        class_performance = self.get_class_performance()
        
        # Recent activities
        recent_activities = self.get_recent_activities()
        
        # Top interest categories
        top_interests = self.get_top_interests()
        
        context.update({
            'total_students': total_students,
            'completed_tests': completed_tests,
            'pending_tests': pending_tests,
            'in_progress_tests': in_progress_tests,
            'completion_rate': completion_rate,
            'overall_average': overall_average,
            'interest_distribution': json.dumps(interest_distribution),
            'class_performance': json.dumps(class_performance),
            'recent_activities': recent_activities,
            'top_interests': top_interests,
            'current_date': timezone.now().strftime('%d %B %Y'),
        })
        
        return context
    
    def get_interest_distribution(self):
        """Get interest distribution data for pie chart"""
        completed_scores = RMIBScore.objects.filter(is_completed=True)
        
        if not completed_scores.exists():
            return {
                'labels': ['Scientific', 'Medical', 'Social Service', 'Computational', 'Others'],
                'data': [28, 22, 18, 15, 17],
                'colors': ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444']
            }
        
        # Calculate highest scores for each student
        interest_counts = {
            'Scientific': 0, 'Medical': 0, 'Social Service': 0, 'Computational': 0,
            'Personal': 0, 'Aesthetic': 0, 'Literary': 0, 'Musical': 0,
            'Outdoor': 0, 'Mechanical': 0, 'Clerical': 0, 'Practical': 0
        }
        
        for score in completed_scores:
            scores_dict = {
                'Scientific': score.scientific,
                'Medical': score.medical,
                'Social Service': score.social_service,
                'Computational': score.computational,
                'Personal': score.personal,
                'Aesthetic': score.aesthetic,
                'Literary': score.literary,
                'Musical': score.musical,
                'Outdoor': score.outdoor,
                'Mechanical': score.mechanical,
                'Clerical': score.clerical,
                'Practical': score.practical,
            }
            
            # Get the highest score category
            highest_category = max(scores_dict, key=scores_dict.get)
            interest_counts[highest_category] += 1
        
        # Get top 5 categories
        sorted_interests = sorted(interest_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'labels': [item[0] for item in sorted_interests],
            'data': [item[1] for item in sorted_interests],
            'colors': ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444']
        }
    
    def get_class_performance(self):
        """Get class performance data for bar chart"""
        classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')
        
        class_data = []
        for class_name in classes:
            students_in_class = Student.objects.filter(student_class=class_name)
            completed_in_class = RMIBScore.objects.filter(
                student__student_class=class_name, 
                is_completed=True
            )
            
            if completed_in_class.exists():
                # Calculate average score for the class
                avg_scores = completed_in_class.aggregate(
                    avg_scientific=Avg('scientific'),
                    avg_medical=Avg('medical'),
                    avg_social_service=Avg('social_service'),
                    avg_computational=Avg('computational'),
                )
                
                individual_avgs = [v for v in avg_scores.values() if v is not None]
                class_average = round(sum(individual_avgs) / len(individual_avgs) if individual_avgs else 0, 1)
            else:
                class_average = 0
            
            class_data.append({
                'class': class_name,
                'average': class_average,
                'total_students': students_in_class.count(),
                'completed': completed_in_class.count()
            })
        
        return {
            'labels': [item['class'] for item in class_data],
            'data': [item['average'] for item in class_data],
            'colors': ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#6366F1']
        }
    
    def get_recent_activities(self):
        """Get recent system activities"""
        activities = []
        
        # Recent completed tests
        recent_tests = RMIBScore.objects.filter(
            is_completed=True, 
            updated_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-updated_at')[:10]
        
        for test in recent_tests:
            # Get highest score
            scores = {
                'Scientific': test.scientific, 'Medical': test.medical,
                'Social Service': test.social_service, 'Computational': test.computational,
            }
            highest_score = max(scores, key=scores.get)
            highest_value = scores[highest_score]
            
            activities.append({
                'type': 'test_completed',
                'student_name': test.student.name,
                'description': f'Menyelesaikan tes RMIB - Kelas {test.student.student_class}',
                'detail': f'Skor tertinggi: {highest_score} ({highest_value})',
                'timestamp': test.updated_at,
                'icon_color': 'green'
            })
        
        # Recent student registrations
        recent_students = Student.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:5]
        
        for student in recent_students:
            activities.append({
                'type': 'student_added',
                'student_name': student.name,
                'description': f'Siswa baru ditambahkan - Kelas {student.student_class}',
                'detail': 'Siap untuk tes RMIB',
                'timestamp': student.created_at,
                'icon_color': 'blue'
            })
        
        # Sort by timestamp and return latest 5
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:5]
    
    def get_top_interests(self):
        """Get top interest categories with statistics"""
        completed_scores = RMIBScore.objects.filter(is_completed=True)
        
        if not completed_scores.exists():
            return [
                {'name': 'Scientific', 'description': 'Penelitian & Eksperimen', 'count': 45, 'percentage': 28.8},
                {'name': 'Medical', 'description': 'Kesehatan & Pengobatan', 'count': 35, 'percentage': 22.4},
                {'name': 'Social Service', 'description': 'Layanan Masyarakat', 'count': 29, 'percentage': 18.6},
                {'name': 'Computational', 'description': 'Perhitungan & Analisis', 'count': 23, 'percentage': 14.7}
            ]
        
        interest_counts = {}
        total_students = completed_scores.count()
        
        categories = {
            'scientific': {'name': 'Scientific', 'description': 'Penelitian & Eksperimen'},
            'medical': {'name': 'Medical', 'description': 'Kesehatan & Pengobatan'},
            'social_service': {'name': 'Social Service', 'description': 'Layanan Masyarakat'},
            'computational': {'name': 'Computational', 'description': 'Perhitungan & Analisis'},
            'personal': {'name': 'Personal', 'description': 'Hubungan Personal'},
            'aesthetic': {'name': 'Aesthetic', 'description': 'Seni & Keindahan'},
        }
        
        for category_field, category_info in categories.items():
            # Count students whose highest score is in this category
            count = 0
            for score in completed_scores:
                student_scores = {
                    'scientific': score.scientific,
                    'medical': score.medical,
                    'social_service': score.social_service,
                    'computational': score.computational,
                    'personal': score.personal,
                    'aesthetic': score.aesthetic,
                }
                
                if max(student_scores, key=student_scores.get) == category_field:
                    count += 1
            
            if count > 0:
                interest_counts[category_field] = {
                    'name': category_info['name'],
                    'description': category_info['description'],
                    'count': count,
                    'percentage': round((count / total_students) * 100, 1)
                }
        
        # Sort by count and return top 4
        sorted_interests = sorted(interest_counts.values(), key=lambda x: x['count'], reverse=True)[:4]
        return sorted_interests
