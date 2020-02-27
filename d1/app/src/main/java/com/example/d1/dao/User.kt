package com.example.d1.dao

data class User(var about_me: String, var bracket_users: List<Int>,
           var brackets: List<Int>, var email: String,var id:Int,
           var last_seen: String,var password_hash:String,var posts:List<String>,
           var username:String)