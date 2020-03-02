package com.example.d1.login

import android.content.Intent
import android.os.AsyncTask
import android.os.Bundle
import android.view.MenuItem
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.example.d1.MainActivity
import com.example.d1.R
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
        val login = findViewById<Button>(R.id.login) as Button
        //val loading = findViewById<ProgressBar>(R.id.loading) as ProgressBar


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
        println("=========================================")
        //http://10.0.2.2:5000/match/1 //android simulator should use 10.0.2.2 replace 127.0.0.1
        val request = Request.Builder()
            .url("http://192.168.0.33:5000/api/user/1")
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
                        println("Password correct")

                        val myIntent = Intent(applicationContext, MainActivity::class.java)
                        //return user json
                        myIntent.putExtra("user",json.toString())
                        startActivityForResult(myIntent, 0)
                        finish()
                    }

                    println("=========================================")

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

