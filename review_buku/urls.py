from django.urls import path
from . import views
app_name = "review_buku"

urlpatterns = [
    path('review/<int:id>/', views.review, name='review'),  # Tambahkan id sebagai parameter
    path('show/<int:id>/', views.show_reviews, name='show_reviews'),  # Tambahkan id sebagai parameter
    path('show-review-json/<int:id>/', views.show_review_json, name='show_review_json'),
    path('get-book-json/<int:id>/', views.get_books_json_by_id, name='get_books_json_by_id'),
    path('show-returned-json/', views.show_returned_json, name='show_returned_json'),
    path('post_review/', views.post_review, name='post_review'),
    path('post-review-flutter/', views.post_review_flutter, name='post_review_flutter'),
]

