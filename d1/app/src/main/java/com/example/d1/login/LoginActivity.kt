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
import android.widget.Toast
import com.android.volley.toolbox.JsonObjectRequest
import okhttp3.*
import org.json.JSONObject

import java.io.IOException;


class LoginActivity : AppCompatActivity() {
    var client = OkHttpClient()


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_login)
        val username = findViewById<EditText>(R.id.username) as EditText
        val password = findViewById<EditText>(R.id.password) as EditText
        val text = findViewById<TextView>(R.id.textView2) as TextView
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
        run(nameStr, passStr)
    }

    fun run(nameStr: String, passStr: String) {
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
        println("=========================================")
        //http://10.0.2.2:5000/match/1 //android simulator should use 10.0.2.2 replace 127.0.0.1
        val request = Request.Builder()
            .url("http://10.0.2.2:5000/user/1")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("==============FAIL==========")
                e.printStackTrace()

            }

            //http response
            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")
                    val text = findViewById<TextView>(R.id.textView2)
                    val json = JSONObject(response.body!!.string())

                    if (nameStr.isEmpty() && passStr.isEmpty()){
                        // user has correct emial and password go back to homescreen

                        val myIntent = Intent(applicationContext, MainActivity::class.java)
                        //return user json
                        myIntent.putExtra("json",json.toString())
                        startActivityForResult(myIntent, 0)
                        finish()
                    }

                    println("=========================================")
                    text.text = "Response: "+json

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

