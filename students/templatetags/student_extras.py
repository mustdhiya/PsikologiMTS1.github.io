from django import template

register = template.Library()

@register.filter
def ordinal(value):
    """Convert integer to ordinal number (1st, 2nd, 3rd, etc.)"""
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value
    
    if 10 <= value % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
    
    return f"{value}{suffix}"

@register.filter
def get_prestasi_type_class(prestasi_type):
    """Get CSS class for prestasi type"""
    classes = {
        'akademik': 'bg-blue-100 text-blue-800',
        'olahraga': 'bg-green-100 text-green-800', 
        'seni': 'bg-purple-100 text-purple-800',
        'organisasi': 'bg-yellow-100 text-yellow-800',
        'teknologi': 'bg-indigo-100 text-indigo-800',
        'keagamaan': 'bg-teal-100 text-teal-800'
    }
    return classes.get(prestasi_type, 'bg-gray-100 text-gray-800')

@register.filter
def get_prestasi_type_icon(prestasi_type):
    """Get icon for prestasi type"""
    icons = {
        'akademik': '🎓',
        'olahraga': '🏃',
        'seni': '🎨', 
        'organisasi': '👥',
        'teknologi': '💻',
        'keagamaan': '🕌'
    }
    return icons.get(prestasi_type, '🏆')

@register.filter
def get_tingkat_class(tingkat):
    """Get CSS class for prestasi tingkat"""
    classes = {
        'sekolah': 'bg-blue-100 text-blue-700',
        'kecamatan': 'bg-green-100 text-green-700',
        'kabupaten': 'bg-yellow-100 text-yellow-700', 
        'provinsi': 'bg-orange-100 text-orange-700',
        'nasional': 'bg-red-100 text-red-700',
        'internasional': 'bg-purple-100 text-purple-700'
    }
    return classes.get(tingkat, 'bg-gray-100 text-gray-700')
