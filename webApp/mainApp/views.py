#webApp/mainApp/views.py 
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
from bson import ObjectId
import certifi
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from bson import ObjectId
from django.http import JsonResponse
from django.utils import timezone
import os
from .decorators import custom_login_required
from django.core.paginator import Paginator
uri=os.getenv('MONGODB_URI')

client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
db = client.NLPulseQA
raw_data_collection = db.rawData
qa_data_collection = db.QAdatas
admin_collection = db.admins 

def index(request):
    return render(request, 'mainApp/index.html')

def submit(request):
    last_submit_time = request.session.get('last_submit_time')
    if last_submit_time:
        last_submit_time = datetime.fromisoformat(last_submit_time)
        if timezone.now() - last_submit_time > timedelta(hours=6):
            request.session['progress_count'] = 0

    progress_count = request.session.get('progress_count', 0)

    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        category = request.POST.get('category')
        change_date = timezone.now()

        try:
            raw_data_collection.insert_one({
                'question': question,
                'answers': [answer],
                'category': category,
                'change_date': change_date
            })
            
            progress_count += 1
            request.session['progress_count'] = progress_count
            request.session['last_submit_time'] = timezone.now().isoformat()

            messages.success(request, 'Soru başarıyla eklendi.')

            return redirect('submit')
        except Exception as e:
            messages.error(request, f'Bir hata oluştu: {str(e)}')

    context = {
        'progress_count': progress_count,
        'progress_steps': range(1, 7)
    }
    return render(request, 'mainApp/submit.html', context)

def validate(request):
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        if question_id:
            question = qa_data_collection.find_one({'_id': ObjectId(question_id)})
            if question:
                if 'true_button' in request.POST or 'false_button' in request.POST:
                    true_count = question.get('true_count', [0])
                    false_count = question.get('false_count', [0])
                    confirmation_count = question.get('confirmation_count', [0])
                    rate = question.get('rate', [0])

                    if isinstance(true_count, int):
                        true_count = [true_count]
                    if isinstance(false_count, int):
                        false_count = [false_count]
                    if isinstance(confirmation_count, int):
                        confirmation_count = [confirmation_count]
                    if isinstance(rate, (int, float)):
                        rate = [rate]

                    if 'true_button' in request.POST:
                        true_count[0] += 1
                    elif 'false_button' in request.POST:
                        false_count[0] += 1
                    
                    confirmation_count[0] += 1
                    rate[0] = true_count[0] / confirmation_count[0] if confirmation_count[0] > 0 else 0

                    qa_data_collection.update_one(
                        {'_id': ObjectId(question_id)},
                        {'$set': {
                            'true_count': true_count,
                            'false_count': false_count,
                            'confirmation_count': confirmation_count,
                            'rate': rate
                        }}
                    )
                elif 'send_selected_answers' in request.POST:
                    answers = question.get('answers', [])
                    true_count = question.get('true_count', [0] * len(answers))
                    false_count = question.get('false_count', [0] * len(answers))
                    confirmation_count = question.get('confirmation_count', [0] * len(answers))
                    rate = question.get('rate', [0] * len(answers))

                    for index in range(len(answers)):
                        response = request.POST.get(f'answer-{index}')
                        if response == 'true':
                            true_count[index] += 1
                        elif response == 'false':
                            false_count[index] += 1
                        confirmation_count[index] += 1
                        rate[index] = true_count[index] / confirmation_count[index] if confirmation_count[index] > 0 else 0

                    qa_data_collection.update_one(
                        {'_id': ObjectId(question_id)},
                        {'$set': {
                            'true_count': true_count,
                            'false_count': false_count,
                            'confirmation_count': confirmation_count,
                            'rate': rate
                        }}
                    )
                elif 'add_button' in request.POST:
                    new_answer = request.POST.get('yourAnswer')
                    answers = question.get('answers', [])
                    answers.append(new_answer)

                    true_count = question.get('true_count', [0] * len(answers))
                    false_count = question.get('false_count', [0] * len(answers))
                    confirmation_count = question.get('confirmation_count', [0] * len(answers))
                    rate = question.get('rate', [0] * len(answers))

                    true_count.append(0)
                    false_count.append(0)
                    confirmation_count.append(0)
                    rate.append(0)

                    qa_data_collection.update_one(
                        {'_id': ObjectId(question_id)},
                        {'$set': {
                            'answers': answers,
                            'true_count': true_count,
                            'false_count': false_count,
                            'confirmation_count': confirmation_count,
                            'rate': rate,
                            'category': question.get('category', ''),
                            'yeni_cevap_eklendi': True
                        }}
                    )
                    updated_question = qa_data_collection.find_one({'_id': ObjectId(question_id)})
                    raw_data_collection.insert_one(updated_question)
                    qa_data_collection.delete_one({'_id': ObjectId(question_id)})

                return redirect('validate')

    random_question_cursor = qa_data_collection.aggregate([{ '$sample': { 'size': 1 } }])
    random_question_list = list(random_question_cursor)
    
    if random_question_list:
        random_question = random_question_list[0]
        question_id = random_question['_id']
        question_text = random_question.get('question', '')
        answers = random_question.get('answers', [])
        true_count = random_question.get('true_count', [0])
        false_count = random_question.get('false_count', [0])
        confirmation_count = random_question.get('confirmation_count', [0])
        rate = random_question.get('rate', [0])
        num_answers = len(answers)
        enumerated_answers = list(enumerate(answers))   
        return render(request, 'mainApp/validate.html', {
            'question_id': str(question_id),
            'question_text': question_text,
            'answer_text': answers[0] if answers else '',  # İlk cevabı göster
            'true_count': true_count,
            'false_count': false_count,
            'confirmation_count': confirmation_count,
            'rate': rate,
            'answers': answers,
            'num_answers': num_answers,
            'enumerated_answers': enumerated_answers
        })
    else:
        return HttpResponse('Veri bulunamadı.')

@custom_login_required
def approve_question(request, question_id):
    question = raw_data_collection.find_one({'_id': ObjectId(question_id)})
    if question:
        if question.get('yeni_cevap_eklendi', False):
            question['approval_date'] = datetime.now()
            question['admin_id'] = request.session.get('admin_id')
            qa_data_collection.insert_one(question)
        else:
            question['approval_date'] = datetime.now()
            question['admin_id'] = request.session.get('admin_id')
            question['confirmation_count'] = [0]
            question['rate'] = [0]
            question['true_count'] = [0]
            question['false_count'] = [0]
            question['category'] = question['category']
            question['change_date'] = question['change_date']

            qa_data_collection.insert_one(question)

        raw_data_collection.delete_one({'_id': ObjectId(question_id)})
    return redirect('admin_panel')

@custom_login_required
def delete_question(request, question_id):
    question = raw_data_collection.find_one({'_id': ObjectId(question_id)})
    
    if question:
        if question.get('yeni_cevap_eklendi', False):
            answers = question.get('answers', [])
            true_count = question.get('true_count', [])
            false_count = question.get('false_count', [])
            confirmation_count = question.get('confirmation_count', [])
            rate = question.get('rate', [])

            if answers:
                answers.pop()
                true_count.pop()
                false_count.pop()
                confirmation_count.pop()
                rate.pop()

                qa_data_collection.insert_one({
                    'question': question['question'],
                    'answers': answers,
                    'true_count': true_count,
                    'false_count': false_count,
                    'confirmation_count': confirmation_count,
                    'category': question['category'],
                    'change_date': question['change_date'],
                    'approval_date': datetime.now(),
                    'admin_id': request.session.get('admin_id'),
                    'rate': rate
                })
                
                raw_data_collection.delete_one({'_id': ObjectId(question_id)})
            else:
                raw_data_collection.delete_one({'_id': ObjectId(question_id)})
        else:
            raw_data_collection.delete_one({'_id': ObjectId(question_id)})
    else:
        messages.error(request, 'Soru bulunamadı.')
    
    return redirect('admin_panel')

@custom_login_required
def admin_panel(request):
    admin_id = request.session.get('admin_id')
    if admin_id:
        questions = list(raw_data_collection.find())
        for question in questions:
            question['id'] = str(question.pop('_id'))
            if question.get('yeni_cevap_eklendi', False):
                question['old_answers'] = question.get('answers', [])[:-1]
                question['new_answer'] = question.get('answers', [])[-1] if len(question['answers']) > 0 else ''
            else:
                question['old_answers'] = None
                question['new_answer'] = None
        return render(request, 'mainApp/admin_panel.html', {'questions': questions})
    else:
        return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        admin = admin_collection.find_one({'username': username, 'password': password})
        if admin:
            request.session['admin_id'] = str(admin['_id'])
            request.session['username'] = admin['username']
            return redirect('admin_panel')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya parola.')

    return render(request, 'mainApp/login.html')

@custom_login_required
def logout_view(request):
    request.session.flush()
    return redirect('login')
from django.core.paginator import Paginator

@custom_login_required
def data_view(request):
    collection = request.GET.get('collection', 'QA_data')
    page = request.GET.get('page', 1)
    
    if collection == 'QA_data':
        data = list(qa_data_collection.find().limit(10).skip((int(page) - 1) * 10))
    else:
        data = list(raw_data_collection.find().limit(10).skip((int(page) - 1) * 10))
    
    for item in data:
        item['_id'] = str(item['_id'])
        if 'change_date' in item:
            item['change_date'] = item['change_date'].strftime('%Y-%m-%d %H:%M:%S')
        if 'approval_date' in item:
            item['approval_date'] = item['approval_date'].strftime('%Y-%m-%d %H:%M:%S')
    
    return render(request, 'mainApp/data_view.html', {
        'data': data,
        'collection': collection,
        'page': int(page),
    })