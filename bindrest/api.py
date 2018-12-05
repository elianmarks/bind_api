# -*- coding: utf-8 -*-
#Elliann Marks
#elian.markes@gmail.com
#

#Bibliotecas
from flask import render_template
from restapp import app, requires_auth, get_post_data, getUser
from restapp import run_and_response, resp_success, run_and_response_info, resp_success_info
from cli import dnsCommands
from cli.moduleLog import logInfo
from cli.moduleLog import logWarn
from cli.moduleLog import logError
import yaml 
import os
import ast

@app.route("/doc")
def showdoc():
    try:
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doc/api.yml")
        apis = yaml.load(open(filename))
        return render_template("doc.html", apis=apis['apis'])
    
    except Exception as er:
        logError(str(er))
        return str(er)

@app.route("/dnscreate", methods=["POST"])
@requires_auth(['bindroot', 'bindadmin'])
def dns_create():
    try:
        with_externo = ast.literal_eval(str(get_post_data('externo', False)))
        if with_externo:
            environment = "externo"
        else:
            environment = "interno"
        nameDomain = get_post_data('nameDomain')
        confReversoHost = get_post_data('confReversoHost')
        confReversoHostTemp = list()
        for confReversoHostTempString in confReversoHost.split(","):
            if confReversoHostTempString.find(":") == -1:
                confReversoHostTemp.append(confReversoHostTempString + ":80")
            else:
                confReversoHostTemp.append(confReversoHostTempString)
        confReversoHost = confReversoHostTemp
        if nameDomain != None and nameDomain.find(".") == -1 and len(nameDomain) >= 1:
            if confReversoHost != None and confReversoHost != "":
                return run_and_response(dnsCommands.create, [environment, nameDomain, getUser(), confReversoHost])
            else:
                logWarn("dnscreate - confReversoHost %s invalid | User-%s"  % (confReversoHost, getUser()))
                return resp_success(["dnscreate - confReversoHost %s invalid | User-%s"  % (confReversoHost, getUser()), False])
        else:
            logWarn("dnscreate - nameDomain %s invalid | User-%s" % (nameDomain, getUser()))
            return resp_success(["dnscreate - nameDomain %s invalid | User-%s" % (nameDomain, getUser()), False])
    
    except Exception as er:
        logError(str(er))
        return resp_success([str(er), False])

@app.route("/dnsdelete", methods=["POST"])
@requires_auth(['bindroot'])
def dns_delete():
    try:
        nameDomain = get_post_data('nameDomain')
        if nameDomain != None and nameDomain.find(".") == -1 and len(nameDomain) >= 1:
            return run_and_response(dnsCommands.delete, [nameDomain, getUser()])
        else:
            logWarn("dnsdelete - nameDomain invalid | User-%s" %getUser())
            return resp_success(["dnsdelete - nameDomain invalid | User-%s" %getUser(), False])
    
    except Exception as er:
        logError(str(er))
        return resp_success([str(er), False])

@app.route("/dnsinfo", methods=["POST"])
@requires_auth(['bindroot', 'bindadmin', 'binduser'])
def dns_info():
    try:
        nameDomain = get_post_data('nameDomain')
        if nameDomain != None and nameDomain.find(".") == -1 and len(nameDomain) >= 1:
            return run_and_response_info(dnsCommands.info, [nameDomain, getUser()])
        else:
            logWarn("dnsinfo - nameDomain invalid | User-%s" %getUser())
            return resp_success_info(["dnsinfo - nameDomain invalid | User-%s" %getUser(), False, None])
    
    except Exception as er:
        logError(str(er))
        return resp_success_info([str(er), False, None])

@app.route("/reversereload", methods=["GET"])
@requires_auth(['bindroot', 'bindadmin'])
def reverse_reload():
    try:
        return run_and_response(dnsCommands.reverseReload, [getUser()])

    except Exception as er:
        logError(str(er))
        return resp_success([str(er), False])
