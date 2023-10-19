from django.shortcuts import render
from django.http import HttpResponseRedirect, FileResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .helpers import generate_random_id
from .models import Class
import qrcode
from datetime import datetime
import csv
from qr_attendance_system import settings


# Create your views here.
@login_required(login_url='login')
def dashboard(request):
    class_list = []
    user = request.user
    classes = Class.objects.filter(user=user).order_by('-created_on', 'name')
    class_length = 0
    for clas in classes:
        class_length += 1
        with open(f'{clas.sheet}', 'r') as csv_file:
            reader = csv.reader(csv_file)
            data = list(reader)
        class_list.append([str(clas.name), clas.qr_id, data])

    print(class_list)
    context = {"class_list": class_list, "length": class_length}
    return render(request, "attendance/dashboard.html", context)

@login_required(login_url='login')
def create(request):
    if request.method == 'POST':
        classname = request.POST.get('classname')
        if classname != None and classname != '':
            current_user = request.user
            qr_id = generate_random_id()
            
            #classes = Class.objects.filter(qr_id=qr_id)
            #while classes != None:
                #qr_id = generate_random_id()
                #classes = Class.objects.filter(qr_id=qr_id)

            qr_image = qrcode.make(f"http://127.0.0.1:8000/scan/{qr_id}")
            qr_image.save(f"temp/qrcodeimages/qrcode_{qr_id}.jpg")
            sheet = open(f'temp/attendancesheets/attendance_{qr_id}.csv', 'w') 
            writer = csv.writer(sheet)
            header = ['S/N', 'Full Name', 'Matric. No.']
            writer.writerow(header)
            sheet.close()
            attendance_class = Class(name=classname, user=current_user, qr_id=qr_id)
            attendance_class.qr_image = f'temp/qrcodeimages/qrcode_{qr_id}.jpg'
            attendance_class.sheet = f'temp/attendancesheets/attendance_{qr_id}.csv'
            attendance_class.save()
            
        else:
            return render(request, "attendance/dashboard.html", {
                "error": "Error created class. Classname cannot be null."
            })
    return HttpResponseRedirect(reverse('dashboard'))

def delete(request, id):
    classes = Class.objects.filter(qr_id=id)
    if classes == None:
        return HttpResponseRedirect(reverse('dashboard'))
    for a_class in classes:
        a_class.delete()
    return HttpResponseRedirect(reverse('dashboard'))

def download_qr(request, id):
    qrpath = str(settings.BASE_DIR) + f'/temp/qrcodeimages/qrcode_{id}.jpg'
    response = FileResponse(open(qrpath, 'rb'))
    return response

def download_attendance(request, id):
    sheetpath = str(settings.BASE_DIR) + f'/temp/attendancesheets/attendance_{id}.csv'
    response = FileResponse(open(sheetpath, 'rb'))
    return response

def addstudent(request, id):
    if request.method == 'POST':
        student_name = request.POST.get('studentname')
        matric_no = request.POST.get('matricno')
        if student_name != '' and matric_no != '':
            sheetpath = str(settings.BASE_DIR) + f'/temp/attendancesheets/attendance_{id}.csv'
            line_count = -1
            with open(sheetpath) as sheet:
                reader = csv.reader(sheet, delimiter=",")
                for row in reader:
                    line_count += 1
            with open(sheetpath, mode='a') as sheet:
                writer = csv.writer(sheet)
                writer.writerow([str(line_count), str(student_name), str(matric_no)])
            return render(request, "attendance/addstudents.html", {
                "message": "Student added successfully! You can add another!",
                "id": id
            })
        else:
            return render(request, "attendance/addstudents.html", {
                "error": "Enter full name and matriculation number!",
                "id": id
            })

    return render(request, "attendance/addstudents.html", {
        "id": id
    })

def log_attendance(request, id):
    if request.method == 'POST':
        matric_no = request.POST.get('matricno')
        if matric_no != '':
            data = []
            sheetpath = str(settings.BASE_DIR) + f'/temp/attendancesheets/attendance_{id}.csv'
            date = str(datetime.now().date())
            date_exists = False
            line_count = 0
            with open(sheetpath) as sheet:
                reader = csv.reader(sheet)
                for row in reader:
                    if line_count == 0:
                        for field in row:
                            if field == date:
                                date_exists = True
                                break
                        line_count += 1
                    data.append(row)

            if date_exists == False:
                data[0].append(date)
                with open(sheetpath, mode="w") as sheet:
                    writer = csv.writer(sheet)
                    writer.writerows(data)

            line_count = -1
            matric_exists = False
            student_row = []
            with open(sheetpath) as sheet:
                reader = csv.reader(sheet)
                for row in reader:
                    line_count += 1
                    print(f"{row[2]}, {matric_no}")
                    if str(row[2]) == str(matric_no):
                        matric_exists = True
                        student_row = row
                        break
                    
            
            if matric_exists == False:
                return render(request, "attendance/scan.html", {
                    "error": "You matriculation number does not exist in the class list. Please if the number you entered is correct or contact your lecturer."
                })
            
            column_number = 0
            
            with open(sheetpath) as sheet:
                reader = csv.reader(sheet)
                count = 0
                for row in reader:
                    for field in row:
                        if field == date:
                            break
                        else:
                            column_number += 1
                    count += 1
                    if count > 0:
                        break

            print(line_count)

            if len(data[line_count])-1 == column_number:
                print("doneeee")
                return HttpResponseRedirect(reverse('dashboard'))
                        
            while len(data[line_count])-1 < column_number-1:
                data[line_count].append('')
            
            if request.session.has_key('matric'):
                if request.session['matric'] == matric_no:
                    pass
                else:
                    return render(request, "attendance/scan.html", {
                        "error": "You cannot sign with multiple matriculation numbers"
                    })
            else:
                request.session['matric'] = matric_no

            data[line_count].append('1')
            with open(sheetpath, mode="w") as sheet:
                writer = csv.writer(sheet)
                writer.writerows(data)

            return render(request, "attendance/scan.html", {
                "message": "Your attendance has been recorded successfully!"
            })

        else:
            return render(request, "attendance/scan.html", {
                "error": "Enter your maticulation number"
            })
            

    return render(request, "attendance/scan.html", {
        "id": id
    })
    



