import fs from "fs";
import ip from "ip";
import express from "express";
import bodyParser from "body-parser";
import nodemailer from "nodemailer";
import fetch from 'node-fetch';

var app=express();
var urlencodedParser = bodyParser.json({ extended: false });
const options = JSON.parse(fs.readFileSync('./config/options.json', 'utf-8'));

let notif={
	heartbeat:{},
	init:()=>{
		console.log("start");
		notif.route();
	},
	getOptions:type=>{
		return options[type];
	},
	route:()=>{
		app.post("/",urlencodedParser,(req,res)=>{
			console.log("notif.heartbeat:",Object.keys(notif.heartbeat));
			const _req=JSON.parse(JSON.stringify(req.body));
			if(!_req?.type){
				res.json({"success":false});
				return;
			}

			if(_req.type=="offline"){
				if(_req.id&&notif.heartbeat["id_"+_req.id]){
					clearTimeout(notif.heartbeat["id_"+_req.id]);
					delete notif.heartbeat["id_"+_req.id];
				}
				if(_req.subtype&&_req.subtype=="heartbeat"&&_req.notif_offline_interval){
					notif.heartbeat["id_"+_req.id]=setTimeout((info)=>{
						if(info.enable_wechat&&info.url_wechat){
							notif.notif_wechat(info);
						}
						if(info.enable_email&&info.email){
							notif.notif_email(info);
						}
						delete notif.heartbeat["id_"+_req.id];
					},1000*60*(Math.max(parseInt(_req.notif_offline_interval),31)),_req);
				}else if(_req.subtype&&_req.subtype=="error"){
					if(_req.enable_wechat&&_req.url_wechat){
						notif.notif_wechat(_req);
					}
					if(_req.enable_email&&_req.email){
						notif.notif_email(_req);
					}
				}
				res.json({"success":true});
				return;
			}else if(_req.type=="email"){
				notif.notif_email(_req);
				res.json({"success":true});
				return;
			}
			res.json({"success":"false, unknown"});
		})
	},
	notif_wechat:async info=>{
		const url = info.url_wechat;
		const data = {
		    "title":info.title,
		    "content":info.content
		};
		const headers = {'Content-Type': 'application/json'};
		const response = await fetch(url, {
			method: 'post',
			body: JSON.stringify(data),
			headers: headers
		});
		const res = await response.json();
		console.log("notif_wechat response:",res);
	},
	notif_email:info=>{
		function checkObjectValues(obj) {
			return Object.values(obj).every(value => value !== null && value !== undefined && value !== '');
		}
		// create transfer object
		let transporter = nodemailer.createTransport({
			host: notif.getOptions("mail_host"),
			port: notif.getOptions("mail_port"),
			secure: notif.getOptions("mail_secure"),
			auth: {
				user: notif.getOptions("mail_user"),
				pass: notif.getOptions("mail_pass")
			}
		});
		// create mail object
		let mailOptions = {
			from: notif.getOptions("mail_user"),
			to: info.email,
			subject: info.title,
			text: info.content
		};

		if(!checkObjectValues(mailOptions)){return false}

		// send mail
		transporter.sendMail(mailOptions, function(error, info) {
			if (error) {
				console.log(error);
			} else {
				console.log('Email sent: ' + info.response);
			}
		});
	}
}

app.listen(1024,async ()=>{
	notif.init();
	console.log(`server on http://${ip.address()}:1024`);
})