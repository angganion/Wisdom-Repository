from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Buku, Review
from pinjam_buku.models import Pengembalian
from .forms import ReviewForm
from django.core import serializers
import json
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login')  # Tambahkan decorator ini jika Anda memerlukannya
def review(request, id):
    buku = Buku.objects.filter(pk=id).first()
    form = ReviewForm(request.POST or None, initial={'idBuku': id})
    username = request.user.username
    member = request.user.member
    context = {
        'buku': buku,
        'username': username,
        'member': member,
        'form': form,
    }
    return render(request, "review.html", context)

def show_reviews(request, id):
    buku = Buku.objects.get(pk=id)
    reviews = Review.objects.filter(buku=buku)
    return render(request, 'lihat_review.html', {'reviews': reviews, 'buku': buku})
# def show_reviews(request, id):
#     reviews = Review.objects.filter(buku_id=id)  # Mengambil semua ulasan untuk buku dengan ID yang sesuai
#     context = {
#         'review': Review,
#     }
#     return render(request, 'lihat_review.html', {'reviews': reviews})
# def show_reviews(request, id):
#     reviews = Review.objects.filter(buku_id=id)
#     review_list = []
#     for review in reviews:
#         review_list.append({
#             'review_text': review.review_text,
#         })
#     return render(request, 'lihat_review.html', {'review': reviews})

@csrf_exempt
@login_required(login_url='/login')  # Perlu login untuk mengakses view ini
def post_review(request):
    if request.method == "POST":
        
        text = request.POST.get('review_text')
        buku = Buku.objects.get(pk= int(request.POST.get('idBuku')))
        review = Review(review_text=text, buku=buku)
        review.save()
        pengembalian = Pengembalian.objects.filter(idBuku= int(request.POST.get('idBuku')), peminjam = request.user).first()
        pengembalian.review = not pengembalian.review
        pengembalian.save()
        return JsonResponse({"success": True})
    return JsonResponse({"message": "Invalid method"})

@csrf_exempt
def post_review_flutter(request):
    try:
        data = json.loads(request.body)
        review_text = data.get('review_text')
        idBuku = data.get('idBuku')
        idPengembalian = data.get('idPengembalian')

        if not review_text or not idBuku:
            return JsonResponse({"success": False, "message": "Missing data"}, status=400)

        buku = Buku.objects.get(pk=idBuku)
        pengembalian = Pengembalian.objects.get(pk=idPengembalian)

        if not pengembalian or pengembalian.review:
            return JsonResponse({"success": False, "message": "No return entry found or already reviewed"}, status=400)

        review = Review(review_text=review_text, buku=buku)
        review.save()

        pengembalian.review = True
        pengembalian.save()

        return JsonResponse({"success": True}, status=200)

    except Buku.DoesNotExist:
        return JsonResponse({"success": False, "message": "Book not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

def show_review_json(request, id):
    buku = Buku.objects.get(pk=id)
    reviews = Review.objects.filter(buku=buku)
    return HttpResponse(serializers.serialize("json", reviews), content_type="application/json")

def show_returned_json(request):
    pengembalians = Pengembalian.objects.filter(peminjam = request.user, review = False)
    return HttpResponse(serializers.serialize("json", pengembalians), content_type="application/json")

@csrf_exempt
def get_books_json_by_id(request, id):
    buku_list = Buku.objects.filter(pk=id)
    buku_list_json = serializers.serialize('json', buku_list)
    return HttpResponse(buku_list_json, content_type="application/json")
