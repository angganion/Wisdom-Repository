from django.urls import path
from pinjam_buku.views import pinjam_buku_outer, lihatbukudipinjam, get_peminjaman_json, get_peminjaman_json_by_id, pengembalian_by_ajax, show_pengembalian, get_peminjaman_json_id_buku, get_pengembalian_json, create_peminjaman_flutter, create_pengembalian_flutter

app_name = 'pinjam_buku'

urlpatterns = [
    path('details/<int:id>/', pinjam_buku_outer, name='pinjam_buku'),
    path('borrowed/', lihatbukudipinjam, name="list_pinjam"),
    path('peminjamanjson/', get_peminjaman_json, name="get_peminjaman_json"),
    path('peminjamanjsonbyid/<int:id>', get_peminjaman_json_by_id, name="get_peminjaman_json_by_id"),
    path('pengembalianbyajax', pengembalian_by_ajax, name="pengembalian_ajax"),
    path('returned/', show_pengembalian, name="show_pengembalian"),
    path('peminjamanjsonidbuku/<int:id>', get_peminjaman_json_id_buku, name="get_peminjaman_json_id_buku"),
    path('pengembalianjson/', get_pengembalian_json, name="get_pengembalian_json"),
    path('peminjamanflutter/', create_peminjaman_flutter, name="create_peminjaman_flutter"),
    path('pengembalianflutter/', create_pengembalian_flutter, name="create_pengembalian_flutter"),
]