db = connect("mongodb://localhost:27017/admin");

db.auth("davidn", "cisco");

// Switch to the desired database
db = db.getSiblingDB("webservices");

// Insert seed data into collection1
db.webhooks.insertMany([
    {
        "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vMTYzMDc4OTAtZTZmNy0xMWVlLTgxYzgtNGRhY2Q3ZTM4Yjdj",
        "name" : "luke_skywalker",
        "template" : 3
    },
    {
        "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vMjU2MTZhZjAtZjM2Mi0xMWVlLTkyZmYtNWIyMmE5NDdiMGE5",
        "name" : "r2-d2",
        "template" : 1
    },
    {
        "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vMzBhMjNlNTAtZjY4MC0xMWVlLTg2YjMtZjMyODYzOTg5OTNl",
        "name" : "owen_lars",
        "template" : 1
    },
    {
        "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vMWZjZmYxMTAtZjM2Mi0xMWVlLWFlZTItMmQzZTIzNmZiNmQ2",
        "name" : "darth_vader",
        "template" : 1
    },
    {
        "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vYTUyNjdhNjAtMTJjZS0xMWVmLTg2ZjctYjUwODFmYThmNzM0",
        "name" : "c-3po",
        "template" : 1
    },
    {
        "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vMzhkNzcwOTAtMWEyNS0xMWVmLWFiOTUtNGQ1ZTEyM2NhMjFm",
        "name" : "biggs_darklighter",
        "template" : 4
    }
]);

// Insert seed data into collection2
db.templates.insertMany([
    {
        "id" : 1,
        "name" : "Default full template",
        "template" : [
            "<hr>",
            "<h2>{activityType}</h2><br>",
            "<br>",
            "<b>Title:</b> {title}<br>",
            "<b>Member:</b> {member}<br>",
            "<b>Email:</b> {emails}<br>",
            "<b>Platform:</b> {platform}<br>",
            "<b>Date/time:</b> {datetime}<br>",
            "<b>Topics:</b> {topics}<br>",
            "<b>Link:</b> {link}<br>",
            "<b>Summary:</b> {summary}"
        ],
        "type" : "activity"
    },
    {
        "id" : 2,
        "name" : "Partial info template",
        "template" : [
            "<hr>",
            "<h2>{activityType}</h2><br>",
            "<br>",
            "<b>Member:</b> {member}<br>",
            "<b>Email:</b> {emails}<br>",
            "<b>Date/time:</b> {datetime}<br>",
            "<b>Summary:</b> {summary}"
        ],
        "type" : "activity"
    },
    {
        "id" : 3,
        "name" : "Minimal info template",
        "template" : [
            "<hr>",
            "<h2>{activityType}</h2><br>",
            "<br>",
            "<b>Member:</b> {member}<br>",
            "<b>Topics:</b> {topics}<br>",
            "<b>Link:</b> {link}<br>",
            "<b>Summary:</b> {summary}"
        ],
        "type" : "activity"
    },
    {
        "id" : 4,
        "name" : "New members with DevNet account tag",
        "type" : "member",
        "template" : [
            "<hr>",
            "<h2>{activityType}</h2><br>",
            "<br>",
            "<b>email:</b> {email}<br>",
            "<b>id:</b> {provider_id}<br>"
        ]
    }
]);

print("Seed data inserted successfully.");
