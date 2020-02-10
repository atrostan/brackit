package com.example.d1.login

import android.content.Intent
import android.os.AsyncTask
import android.os.Bundle
import android.view.MenuItem
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.Toolbar
import androidx.appcompat.app.ActionBar
import com.example.d1.MainActivity
import com.example.d1.R

import java.io.IOException
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.net.URL


class LoginActivity : AppCompatActivity() {
    private val client = OkHttpClient()


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

        }

        //navigate back
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

    }

    private fun Okhttp(nameStr: String, passStr: String) {
            run()
    }

    fun run() {
//        val request = Request.Builder()
//            .url("https://publicobject.com/helloworld.txt")
//            .build()
//
//        client.newCall(request).execute().use { response ->
//            if (!response.isSuccessful) throw IOException("Unexpected code $response")
//
//            for ((name, value) in response.headers) {
//                println("$name: $value")
//            }
//
//            println(response.body!!.string())
//        }


    }

    override fun onOptionsItemSelected(item: MenuItem?): Boolean {
        val myIntent = Intent(applicationContext, MainActivity::class.java)
        startActivityForResult(myIntent, 0)
        finish()
        return true
    }
}
