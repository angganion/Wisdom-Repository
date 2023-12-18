from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.urls import reverse
from django.contrib import messages
from daftar_buku.models import Buku
from pinjam_buku.models import Peminjaman, Pengembalian
from pinjam_buku.forms import PeminjamanForm
import datetime
import json

# Create your views here.
@login_required(login_url='/login')
def pinjam_buku_outer(request, id):
    buku = Buku.objects.filter(pk=id).first()
    form = PeminjamanForm(request.POST or None, initial={'idBuku': id})
    username = request.user.username
    member = request.user.member
    if member.lower() == "premium":
        hari = 7
    else:
        hari = 3
    hari_kembali = (datetime.datetime.now() + datetime.timedelta(days=hari)).date()
    context = {
        'buku': buku,
        'username': username,
        'member': member,
        'return': hari_kembali,
        'form': form,
    }
    #print(form.is_valid())
    if form.is_valid() and request.method == "POST":
        check = Peminjaman.objects.filter(buku = buku, peminjam=request.user)
        if len(check) != 0:
            messages.warning(request, 'Buku sudah anda pinjam saat ini.')
            return redirect('pinjam_buku:list_pinjam')
        check = Peminjaman.objects.filter(buku = buku)
        if len(check) != 0:
            messages.warning(request, 'Buku sedang dipinjam oleh member lain. Silahkan kembali beberapa saat nanti.')
            return redirect('pinjam_buku:list_pinjam')
        check = Peminjaman.objects.filter(peminjam=request.user)
        if (request.user.member.lower() == "premium"):
            batas = 7
        else:
            batas = 3
        if len(check) >= batas:
            messages.warning(request, 'Batas peminjaman buku sudah tercapai. Silahkan kembalikan beberapa buku yang sudah dipinjam sebelumnya.')
            return redirect('pinjam_buku:list_pinjam')
        peminjaman = form.save(commit=False)
        peminjaman.peminjam = request.user
        peminjaman.buku = buku
        peminjaman.save()
        #print(Peminjaman.objects.all())
        messages.success(request, 'Buku berhasil dipinjam')
        return redirect('pinjam_buku:list_pinjam')
    return render(request, "pinjambuku.html", context)

@login_required(login_url='/login')
def lihatbukudipinjam(request):
    peminjamans = Peminjaman.objects.filter(peminjam = request.user)
    context = {
        'peminjamans': peminjamans
    }
    return render(request, "listbukudipinjam.html", context)

@login_required(login_url='/login')
def get_peminjaman_json(request):
    peminjamans = Peminjaman.objects.filter(peminjam = request.user).values('pk', 'idBuku', 'buku__gambar', 'buku__judul', 'tanggal_dipinjam', 'tanggal_pengembalian')
    peminjaman_list = list(peminjamans)
    return JsonResponse(peminjaman_list, safe=False)

@login_required(login_url='/login')
def get_pengembalian_json(request):
    pengembalians = Pengembalian.objects.filter(peminjam = request.user, review = False).values('pk', 'idBuku', 'buku__gambar', 'buku__judul')
    pengembalian_list = list(pengembalians)
    return JsonResponse(pengembalian_list, safe=False)

@login_required(login_url='/login')
def get_peminjaman_json_by_id(request, id):
    peminjamans = Peminjaman.objects.filter(pk = id).values('pk', 'idBuku', 'buku__gambar', 'buku__judul', 'peminjam__username', 'peminjam__member', 'tanggal_dipinjam', 'tanggal_pengembalian')
    peminjaman_list = list(peminjamans)
    return JsonResponse(peminjaman_list, safe=False)

@login_required(login_url='/login')
@csrf_exempt
def pengembalian_by_ajax(request):
    if request.method == 'POST':
        id_peminjaman = request.POST.get("idPeminjaman")
        id_buku = request.POST.get("idbuku")
        peminjaman = Peminjaman.objects.filter(pk = id_peminjaman, peminjam=request.user).first()
        peminjaman.delete()
        user = request.user
        buku_dikembalikan = Buku.objects.filter(pk = id_buku).first()
        check_pengembalian = Pengembalian.objects.filter(buku = buku_dikembalikan, peminjam=user)
        if len(check_pengembalian) == 0:
            new_pengembalian = Pengembalian(buku = buku_dikembalikan, peminjam = user, idBuku = id_buku, review = False)
            new_pengembalian.save()
            return HttpResponse(b"CREATED", status=201)
        return HttpResponse(b"DELETED PEMINJAMAN", status=201)
    return HttpResponseNotFound()

@login_required(login_url='/login')
def show_pengembalian(request):
    pengembalians = Pengembalian.objects.filter(peminjam = request.user, review = False)
    context = {
        'pengembalians': pengembalians
    }
    return render(request, "listbukureturn.html", context)

@login_required(login_url='/login')
def get_peminjaman_json_id_buku(request, id):
    buku = Buku.objects.filter(pk=id).first()
    username = request.user.username
    member = request.user.member
    if member.lower() == "premium":
        hari = 7
    else:
        hari = 3
    hari_kembali = (datetime.datetime.now() + datetime.timedelta(days=hari)).date()
    peminjaman_buku = Peminjaman.objects.filter(idBuku = id).first()
    if (peminjaman_buku == None):
        can_borrow = True
        is_borrow = False
    else:
        can_borrow = False
        if (peminjaman_buku.peminjam == request.user):
            is_borrow = True
        else:
            is_borrow = False
    check = Peminjaman.objects.filter(peminjam=request.user)
    overlimit = False
    if (request.user.member.lower() == "premium"):
        batas = 7
    else:
        batas = 3
    if len(check) >= batas:
        overlimit = True
    can_borrow_final = can_borrow and (not overlimit) and (not is_borrow)
    return JsonResponse({
            "username": username,
            "member": member,
            "judul": buku.judul,
            "gambar": buku.gambar,
            "kategori": buku.kategori,
            "penulis": buku.penulis,
            "tahun": str(buku.tahun),
            "rating": str(buku.rating.rating),
            "hari_dipinjam": datetime.datetime.now().date().strftime("%B %d, %Y"),
            "hari_kembali": hari_kembali.strftime("%B %d, %Y"),
            "dipinjam": can_borrow,
            "dipinjam_member": is_borrow,
            "overlimit": overlimit,
            "final": can_borrow_final,
        }, status=200)

@csrf_exempt
@login_required(login_url='/login') 
def create_peminjaman_flutter(request):
    try:
        if request.method == 'POST':
            
            data = json.loads(request.body)
            idBuku = int(data["idBuku"])
            buku = Buku.objects.filter(pk=idBuku).first()
            check = Peminjaman.objects.filter(buku = buku, peminjam=request.user)
            if len(check) != 0:
                return JsonResponse({"status": "error"}, status=401)
            check = Peminjaman.objects.filter(buku = buku)
            if len(check) != 0:
                return JsonResponse({"status": "error"}, status=401)
            check = Peminjaman.objects.filter(peminjam=request.user)
            if (request.user.member.lower() == "premium"):
                batas = 7
            else:
                batas = 3
            if len(check) >= batas:
                return JsonResponse({"status": "error"}, status=401)
            new_peminjaman = Peminjaman.objects.create(
                peminjam = request.user,
                idBuku = idBuku,
                buku = buku,
            )

            new_peminjaman.save()

            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({"status": "error"}, status=401)
    except:
        return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
@login_required(login_url='/login') 
def create_pengembalian_flutter(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            idBuku = int(data["idBuku"])
            idPeminjaman = int(data["idPeminjaman"])
            peminjaman = Peminjaman.objects.filter(pk = idPeminjaman, peminjam=request.user).first()
            peminjaman.delete()
            user = request.user
            buku_dikembalikan = Buku.objects.filter(pk = idBuku).first()
            check_pengembalian = Pengembalian.objects.filter(buku = buku_dikembalikan, peminjam=user)
            if len(check_pengembalian) == 0:
                new_pengembalian = Pengembalian.objects.create(
                    buku = buku_dikembalikan,
                    peminjam = user,
                    idBuku = idBuku,
                    review = False
                )
                new_pengembalian.save()

            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({"status": "error"}, status=401)
    except:
        return JsonResponse({"status": "error"}, status=401)