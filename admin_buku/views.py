from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.core.paginator import Paginator, Page
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db.models.functions import Lower
from django.db import transaction
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from daftar_buku.models import Buku, Rating
from daftar_buku.forms import SearchForm
from daftar_buku.views import daftar_genre
from admin_buku.forms import BukuForm, RequestBuku
from admin_buku.models import RequestBuku
import pandas, os, json

def delete_book(request, bookID):
    book = Buku.objects.get(pk=bookID)

    if request.method == 'DELETE':
        book.delete()
        return JsonResponse({'success': True,})
    
def create_book(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn', '')
        judul = request.POST.get('judul', '')
        penulis = request.POST.get('penulis', '')
        tahun = request.POST.get('tahun', 0)  
        kategori = request.POST.get('kategori', '')
        gambar = request.POST.get('gambar', '')
        deskripsi = request.POST.get('deskripsi', '')
        rating_obj = Rating(rating=request.POST.get('rating', 0.0))
        rating_obj.save()

        rating = Rating.objects.get(pk=rating_obj.pk)

        buku = Buku(
            isbn=isbn,
            judul=judul,
            penulis=penulis,
            tahun=tahun,
            kategori=kategori,
            gambar=gambar,
            deskripsi=deskripsi,
            rating=rating
        )

        buku.save()

        return HttpResponse(b"CREATED", status=201)
    
    return HttpResponseNotFound()

def edit_book(request, bookID):
    if request.method == 'POST':
        isbn = request.POST.get('isbn', '')
        judul = request.POST.get('judul', '')
        penulis = request.POST.get('penulis', '')
        tahun = request.POST.get('tahun', 0)  
        kategori = request.POST.get('kategori', '')
        gambar = request.POST.get('gambar', '')
        deskripsi = request.POST.get('deskripsi', '')
        rating = request.POST.get('rating', 0.0)

        buku = Buku.objects.get(pk=bookID)

        rating_obj = buku.rating
        rating_obj.rating = rating
        rating_obj.save()

        rating = Rating.objects.get(pk=rating_obj.pk)

        buku.isbn = isbn
        buku.judul = judul
        buku.penulis = penulis
        buku.tahun = tahun
        buku.kategori = kategori
        buku.gambar = gambar
        buku.deskripsi = deskripsi
        buku.rating = rating

        buku.save()

        return HttpResponse(b"CREATED", status=201)
    
    return HttpResponseNotFound()

@csrf_exempt
def delete_request_book(request, bookID):
    book = RequestBuku.objects.get(pk=bookID)

    if request.method == 'DELETE':
        book.delete()
        return JsonResponse({'success': True,})

@csrf_exempt
def acc_request_book(request, bookID):
    if request.method == 'POST':
        request_buku = RequestBuku.objects.get(pk=bookID)

        isbn = request_buku.isbn
        judul = request_buku.judul
        penulis = request_buku.penulis
        tahun = request_buku.tahun
        kategori = request_buku.kategori
        gambar = request_buku.gambar
        deskripsi = request_buku.deskripsi
        rating = request_buku.rating

        buku = Buku(
            isbn=isbn,
            judul=judul,
            penulis=penulis,
            tahun=tahun,
            kategori=kategori,
            gambar=gambar,
            deskripsi=deskripsi,
            rating=rating,
        )

        buku.save()
        request_buku.delete()

        return HttpResponse(b"CREATED", status=201)
    
    return HttpResponseNotFound()

@csrf_exempt
def create_book_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        rating_obj = Rating.objects.create(
            rating = float(data["rating"])
        )
        rating_obj.save()

        rating = Rating.objects.get(pk=rating_obj.pk)

        buku = Buku(
            isbn=data["isbn"],
            judul=data["judul"],
            penulis=data["penulis"],
            tahun=int(data["tahun"]),
            kategori=data["kategori"],
            gambar=data["gambar"],
            deskripsi=data["deskripsi"],
            rating=rating
        )

        buku.save()

        return JsonResponse({"status": "success"}, status=200)
    
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def edit_book_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        isbn=data["isbn"]
        judul=data["judul"]
        penulis=data["penulis"]
        tahun=int(data["tahun"])
        kategori=data["kategori"]
        gambar=data["gambar"]
        deskripsi=data["deskripsi"]
        rating = float(data["rating"])

        buku = Buku.objects.get(pk=int(data["bookID"]))

        rating_obj = buku.rating
        rating_obj.rating = rating
        rating_obj.save()

        rating = Rating.objects.get(pk=rating_obj.pk)

        buku.isbn = isbn
        buku.judul = judul
        buku.penulis = penulis
        buku.tahun = tahun
        buku.kategori = kategori
        buku.gambar = gambar
        buku.deskripsi = deskripsi
        buku.rating = rating

        buku.save()

        return JsonResponse({"status": "success"}, status=200)
    
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def delete_book_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        book = Buku.objects.get(pk=int(data["bookID"]))
        book.delete()
        return JsonResponse({"status": "success"}, status=200)
        
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def create_request_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        rating_obj = Rating.objects.create(
            rating = float(data["rating"])
        )
        rating_obj.save()

        rating = Rating.objects.get(pk=rating_obj.pk)

        buku = RequestBuku(
            isbn=data["isbn"],
            judul=data["judul"],
            penulis=data["penulis"],
            tahun=int(data["tahun"]),
            kategori=data["kategori"],
            gambar=data["gambar"],
            deskripsi=data["deskripsi"],
            rating=rating,
            user=request.user,
        )

        buku.save()

        return JsonResponse({"status": "success"}, status=200)
    
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def acc_request_book_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        request_buku = RequestBuku.objects.get(pk=int(data["bookID"]))

        isbn=data["isbn"]
        judul=data["judul"]
        penulis=data["penulis"]
        tahun=int(data["tahun"])
        kategori=data["kategori"]
        gambar=data["gambar"]
        deskripsi=data["deskripsi"]
        rating_obj = Rating.objects.create(
            rating = float(data["rating"])
        )
        rating_obj.save()

        rating = Rating.objects.get(pk=rating_obj.pk)
        

        buku = Buku(
            isbn=isbn,
            judul=judul,
            penulis=penulis,
            tahun=tahun,
            kategori=kategori,
            gambar=gambar,
            deskripsi=deskripsi,
            rating=rating,
        )

        buku.save()
        request_buku.delete()

        return JsonResponse({"status": "success"}, status=200)
    
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def delete_request_book_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        book = RequestBuku.objects.get(pk=int(data["bookID"]))
        book.delete()
        return JsonResponse({"status": "success"}, status=200)
        
    return JsonResponse({"status": "error"}, status=401)

def search_books(request):
    if not request.method == 'POST':
        if 'search-books' in request.session:
            if 'search-books' in request.session:
                request.POST = request.session['search-books']
            request.method = 'POST'

    if request.method == 'POST':
        form = SearchForm(request.POST)
        request.session['search-books'] = request.POST

        if form.is_valid():
            query = form.cleaned_data['query']
            buku_list = Buku.objects.filter(Q(judul__icontains=query) | Q(penulis__icontains=query) | Q(kategori__icontains=query))

            paginator = Paginator(buku_list, 12)
            page = request.GET.get('page', 1)

            try:
                buku_list = paginator.page(page)
            except PageNotAnInteger:
                buku_list = paginator.page(1)
            except EmptyPage:
                buku_list = paginator.page(paginator.num_pages)

            return render(request, 'main-admin.html', {'buku': buku_list,
                                                 'genre': daftar_genre,
                                                 })

        else:
            return render(request, 'main-admin.html', {'form': form})
        
def sort_books(request, query):
   
    if request.method == 'GET':

        sort = request.GET.getlist('Sort', request.session.get('Sort'))
        buku_list = Buku.objects.all()
        if query == 'judul':
            buku_list = buku_list.order_by(Lower('judul'))
        if query == 'tahun':
            buku_list = buku_list.order_by('tahun')
        if query == 'rating':
            buku_list = buku_list.order_by('-rating__rating')
        paginator = Paginator(buku_list, 24)  
        page = request.GET.get('page')
        buku = paginator.get_page(page)
        context = {
            'buku': buku,
            'genre' : daftar_genre,
        }
        request.session['Sort'] = sort
        return render(request, 'main-admin.html', context)

def make_buku(request):

    file_path = os.path.join(os.path.dirname(__file__), 'static/books.csv')
    file_csv = open(file_path, 'r', encoding='utf-8')
    data = pandas.read_csv(file_csv, encoding='utf-8')

    buku = {}
    buku['isbn'] = data['isbn13'].tolist()
    buku['judul'] = data['title'].tolist()
    buku['penulis'] = data['authors'].tolist()
    buku['tahun'] = data['published_year'].tolist()
    buku['kategori'] = data['categories'].tolist()
    buku['gambar'] = data['thumbnail'].tolist()
    buku['deskripsi'] = data['description'].tolist()
    buku['rating'] = data['average_rating'].tolist()

    counter = 0

    with transaction.atomic():
        for i in range(0, len(data['isbn13'])):
            try:
                if counter == 100:
                    break
                rating_obj = Rating(rating=buku['rating'][i])
                rating_obj.save()

                rating = Rating.objects.get(pk=rating_obj.pk)
                buku_obj = Buku(isbn=buku['isbn'][i], judul=buku['judul'][i], penulis=buku['penulis'][i], tahun=buku['tahun'][i], kategori=buku['kategori'][i], gambar=buku['gambar'][i], deskripsi=buku['deskripsi'][i], rating=rating)
                buku_obj.save()
                counter += 1
            except:
                print("tesss")
                pass

    return HttpResponseRedirect(reverse('admin_buku:show_main'))

def show_main(request):

    if(len(Buku.objects.all()) == 0):
        make_buku(request)    
    buku_list = Buku.objects.all()
    paginator = Paginator(buku_list, 12)  
    page = request.GET.get('page')
    buku = paginator.get_page(page)
    context = {
        'buku': buku,
        'genre' : daftar_genre
    }
    return render(request, 'main-admin.html', context)

def request_buku(request):
 
    buku_list = RequestBuku.objects.all()
    paginator = Paginator(buku_list, 12)  
    page = request.GET.get('page')
    buku = paginator.get_page(page)
    context = {
        'buku': buku,
        'genre' : daftar_genre
    }
    return render(request, 'request-admin.html', context)

def book_details(request):

    book_id = request.GET.get('id')
    book = Buku.objects.get(id=book_id)

    rating = Rating.objects.get(id=book.rating.pk)
    
    return JsonResponse({'isbn': book.isbn,
                        'judul': book.judul,
                        'penulis': book.penulis,
                        'tahun': book.tahun,
                        'kategori': book.kategori,
                        'gambar': book.gambar,
                        'deskripsi':book.deskripsi,
                        'rating': float(rating.rating)})

def request_book_details(request):

    book_id = request.GET.get('id')
    book = RequestBuku.objects.get(id=book_id)

    rating = Rating.objects.get(id=book.rating.pk)
    
    return JsonResponse({'isbn': book.isbn,
                        'judul': book.judul,
                        'penulis': book.penulis,
                        'tahun': book.tahun,
                        'kategori': book.kategori,
                        'gambar': book.gambar,
                        'deskripsi':book.deskripsi,
                        'rating': float(rating.rating),
                        'user': book.user.pk,})

@csrf_exempt
def get_books_json(request):
    books = Buku.objects.all()
    return HttpResponse(serializers.serialize('json', books),  content_type="application/json")

@csrf_exempt
def get_request_books_json(request):
    books = RequestBuku.objects.all()
    return HttpResponse(serializers.serialize('json', books),  content_type="application/json")

@csrf_exempt
def get_user(request):
    if request.user.is_authenticated:
        return JsonResponse({'username': request.user.username})
    else:
        return JsonResponse({'username': 'Anonymous'})
    
@csrf_exempt
def get_buku_by_author(request):

    if request.method == 'POST':
        form = request.POST.get('query')
        buku = Buku.objects.filter(Q(penulis__icontains=form))
        buku_list_json = serializers.serialize('json', buku)
        return HttpResponse(buku_list_json)