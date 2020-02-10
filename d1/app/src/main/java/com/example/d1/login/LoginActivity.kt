package com.example.d1.login

import android.content.Intent
import android.os.AsyncTask
import android.os.Bundle
import android.view.MenuItem
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.ActionBar
import com.example.d1.MainActivity
import com.example.d1.R
import okhttp3.*

import java.io.IOException;


class LoginActivity : AppCompatActivity() {
    var client = OkHttpClient()


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_login)
        val username = findViewById<EditText>(R.id.username) as EditText
        val password = findViewById<EditText>(R.id.password) as EditText
        val login = findViewById<Button>(R.id.login) as Button
        val loading = findViewById<ProgressBar>(R.id.loading) as ProgressBar



        login.setOnClickListener {
            val nameStr = username.text.toString()
            val passStr = password.text.toString()
            Okhttp(nameStr,passStr)
        }

        //navigate back
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

    }

    private fun Okhttp(nameStr: String, passStr: String) {
        run()
    }

    fun run() {
//        val payload = "test payload"
//
//        val okHttpClient = OkHttpClient()
//        val requestBody = payload.toRequestBody()
//        val request = Request.Builder()
//            .method("POST", requestBody)
//            .url("url")
//            .build()
//        okHttpClient.newCall(request).enqueue(object : Callback {
//            override fun onFailure(call: Call, e: IOException) {
//                // Handle this
//            }
//
//            override fun onResponse(call: Call, response: Response) {
//                // Handle this
//            }
//        })

        val request = Request.Builder()
            .url("https://reqres.in/api/users?page=2")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
            }

            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")

                    for ((name, value) in response.headers) {
                        println("$name: $value")
                    }

                    println(response.body!!.string())

                }
            }
        })
    }


    override fun onOptionsItemSelected(item: MenuItem?): Boolean {
        val myIntent = Intent(applicationContext, MainActivity::class.java)
        startActivityForResult(myIntent, 0)
        finish()
        return true
    }
}

