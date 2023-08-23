from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import openai
import json
from flask import Flask, render_template, request, jsonify
import openai

openai.api_key = "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"

init_messages = {"role": "system", "content": "你将作为一个能够提供帮助的助手."}
msg = []

def add_response(response_text):
    txt = {"role": "assistant", "content": response_text}
    msg.append(txt)


def add_ask(ask):
    txt = {"role": "user", "content": ask}
    print(type(ask))
    msg.append(txt)


def ask_gpt():
    print(msg)
    response = openai.ChatCompletion.create(presence_penalty = 1,frequency_penalty = 1,temperature = 1.0,n = 1,model = "gpt-3.5-turbo",messages = msg)
    print(response)
    return response

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/ac', methods=['POST'])
def chat():
    try:
        print("test......")
        msg.append(init_messages)
        # request.get_json()
        params = request.get_json()
        message_page = params["message"]

        add_ask(message_page.strip())
        public_response = ask_gpt()
        response_text = public_response.choices[0].message.content.strip()
        
        #createTs = public_response.created
        add_response(response_text)

        #print('本次消费的token总数量：' + str(public_response['usage'].total_tokens))
        return jsonify({"data": response_text})
    except Exception as e:
        print("123")
        return jsonify({"error": str(e)})

@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)
