from sqlalchemy import func, asc, delete

from QLPMT.models import User, BenhNhan, DanhSachKham, UserRole, PhieuKhamBenh, ChiTietPhieuKhamBenh, \
    LoaiThuoc, Thuoc, DonVi, BacSi, HoaDon, QuyDinhSoTienKham
from QLPMT import db
import hashlib


def online_register(HoTen, GioiTinh, NamSinh, DiaChi, DanhSachKham_id):
    b = BenhNhan(HoTen=HoTen, GioiTinh=GioiTinh, NamSinh=NamSinh, DiaChi=DiaChi, DanhSachKham_id=DanhSachKham_id)
    db.session.add(b)
    db.session.commit()


# Phieu kham benhbe
def add_medical_report(ngaykham, mabenhnhan, trieuchung, dudoanbenh):
    pk = PhieuKhamBenh(NgayKham=ngaykham, TrieuChung=trieuchung, DuDoanBenh=dudoanbenh, BacSi_id=1,
                       BenhNhan_id=mabenhnhan, HoaDon_id=mabenhnhan)
    db.session.add(pk)
    db.session.commit()


def add_payment(payment_id):
    found = db.session.query(db.session.query(HoaDon.id).filter_by(id=payment_id).exists()).scalar()
    print(found)
    if not found:
        query = db.session.query(func.max(QuyDinhSoTienKham.id))
        hd = HoaDon(id=payment_id, ThuNgan_id=1, SoTienKham_id=query)
        db.session.add(hd)
        db.session.commit()


def add_detail_medical_report(tenloaithuoc, tenthuoc, soluong, cachdung):
    thuoc_id = get_med_id(tenthuoc, tenloaithuoc)
    phieukham_id = (get_medical_report_last_id())
    ctpkb = ChiTietPhieuKhamBenh(SoLuong=soluong, CachDung=cachdung, PhieuKhamBenh_id=phieukham_id,
                                 Thuoc_id=thuoc_id)
    db.session.add(ctpkb)
    db.session.commit()


def load_med_name(med_type=None):
    if med_type:
        return Thuoc.query. \
            filter(Thuoc.LoaiThuoc_id == LoaiThuoc.id).filter(LoaiThuoc.TenLoaiThuoc == med_type).all()
    return Thuoc.query.all()


def load_med_type():
    return LoaiThuoc.query.all()


def load_med_info():
    return db.session.query(Thuoc, LoaiThuoc, DonVi). \
        join(LoaiThuoc, Thuoc.LoaiThuoc_id == LoaiThuoc.id). \
        join(DonVi, Thuoc.DonVi_id == DonVi.id). \
        order_by(Thuoc.id.asc()).all()


def get_med_type_id(med_type):
    return db.session.query(LoaiThuoc.id).filter(LoaiThuoc.TenLoaiThuoc.__eq__(med_type)).all()


def get_med_id(med_name=None, med_type=None):
    return db.session.query(Thuoc.id).filter(LoaiThuoc.TenLoaiThuoc.__eq__(med_type),
                                             Thuoc.TenThuoc.__eq__(med_name),
                                             Thuoc.LoaiThuoc_id.__eq__(LoaiThuoc.id)).scalar()


def get_medical_date_of_patient(patient_id):
    return db.session.query(PhieuKhamBenh, BenhNhan). \
        join(BenhNhan, PhieuKhamBenh.BenhNhan_id.__eq__(BenhNhan.id)). \
        filter(BenhNhan.id.__eq__(patient_id)).all()


def load_detail_medical_report(med_report_id):
    return db.session.query(ChiTietPhieuKhamBenh, PhieuKhamBenh). \
        join(PhieuKhamBenh, ChiTietPhieuKhamBenh.PhieuKhamBenh_id.__eq__(PhieuKhamBenh.id)). \
        filter(PhieuKhamBenh.id == med_report_id).all()


def some_test():
    return db.session.query()


def get_medical_report_last_id():
    return db.session.query(func.max(PhieuKhamBenh.id)).scalar()


def get_payment_last_id():
    return db.session.query(func.max(HoaDon.id)).scalar()


def update_med_amount(med_name, amount):
    db.session.query(Thuoc).filter(Thuoc.TenThuoc.__eq__(med_name)). \
        update({'SoLuongConLai': Thuoc.SoLuongConLai - amount})
    db.session.commit()


def get_med_unit(med_name):
    return db.session.query(DonVi.TenDonVi).join(Thuoc, Thuoc.DonVi_id.__eq__(DonVi.id)). \
        filter(Thuoc.TenThuoc.__eq__(med_name)).scalar()


def get_patient_name(patient_id):
    return db.session.query(BenhNhan.HoTen). \
        filter(BenhNhan.id.__eq__(patient_id)). \
        filter(BenhNhan.DanhSachKham_id.__eq__(db.session.query(func.max(DanhSachKham.id)))).scalar()


# def get_thuocId(name):
#     return db.session.query(Thuoc.id).filter(LoaiThuoc.TenLoaiThuoc.__eq__(name),
#                                                     Thuoc.LoaiThuoc_id.__eq__(LoaiThuoc.id))
# def get_thuoc_by_loaithuoc(name):
#     return db.session.query(Thuoc.id)\
#             .join(LoaiThuoc, Thuoc.LoaiThuoc_id.__eq__(LoaiThuoc.id), isouter=True)\
#              .filter(LoaiThuoc.TenLoaiThuoc.__eq__(name).all())


def count_patient():
    return db.session.query(BenhNhan).count()


def load_BenhNhan():
    return BenhNhan.query.all()


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_phieukhambenn(id):
    return PhieuKhamBenh.query.filter(PhieuKhamBenh.BenhNhan_id == id).all()


def register(name, username, password, avatar, type):
    if type == 'doctor':
        type = UserRole.DOCTOR
    elif type == 'nurse':
        type = UserRole.NURSE
    elif type == 'cashier':
        type = UserRole.CASHIER
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = UserLogin(name=name, username=username.strip(),
                  password=password, image=avatar, user_role=type)
    db.session.add(u)
    db.session.commit()
