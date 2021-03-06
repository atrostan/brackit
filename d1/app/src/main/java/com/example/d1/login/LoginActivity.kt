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
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

import java.io.IOException;


class LoginActivity : AppCompatActivity() {
    var client = OkHttpClient()
    val requestURL = "http://192.168.0.33:5000/api/"

    var USER:String = ""
    var PASS:String=""


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)



        setContentView(R.layout.activity_login)
        val username = findViewById<EditText>(R.id.username) as EditText
        val password = findViewById<EditText>(R.id.password) as EditText
        val login = findViewById<Button>(R.id.login) as Button
        var signup = findViewById<Button>(R.id.register) as Button
        //val loading = findViewById<ProgressBar>(R.id.loading) as ProgressBar


        login.setOnClickListener {
            val nameStr = username.text.toString()
            val passStr = password.text.toString()

            Okhttp(nameStr,passStr,1)

        }

        signup.setOnClickListener{
            val nameStr = username.text.toString()
            val passStr = password.text.toString()

            if (!nameStr.isEmpty() && !passStr.isEmpty() && nameStr.contains("@")){
                Thread{
                    register(nameStr,passStr)
                }.start()

            }


        }

        //navigate back
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

    }

    private fun register(name:String,pass:String){
        val client = OkHttpClient()

        var jobject = JSONObject()
        var username = name.split("@")[0]
        jobject.put("username",username)
        jobject.put("password",pass)
        jobject.put("email",name)

        val mediaType = "application/json; charset=utf-8".toMediaType()

        //192.168.0.33    172.17.184.246
        val request = Request.Builder()
            .url(requestURL+"users")
            .post(jobject.toString().toRequestBody(mediaType))
            .build()

        client.newCall(request).execute().use { response ->
           // if (!response.isSuccessful) throw IOException("Unexpected code $response")

            if (response.code == 400){
                runOnUiThread{
                    Toast.makeText(this@LoginActivity, "User already exist", Toast.LENGTH_SHORT).show()
                }

            }else if (response.code == 201){
                runOnUiThread{
                    Toast.makeText(this@LoginActivity,
                        "Successfully registered", Toast.LENGTH_SHORT).show()
                }

                var userid = response.headers["location"]!!.split("/").takeLast(1)[0]


                getlogin(name,pass)

                Okhttp(name,pass,userid.toInt())
            }else{}



        }
    }

    private fun getlogin(name:String,pass:String){
        var name1 = name.split("@")[0]
        var client = OkHttpClient()

        println(name+"--------------"+pass)

        val request = Request.Builder()
            .url(requestURL+"login")
            .addHeader(name1,pass)
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
                    println(response.body!!.string()+"------------------")

                }
            }
        })




    }


    private fun Okhttp(nameStr: String, passStr: String,id:Int) {
        run(nameStr, passStr,id)
    }

    fun run(nameStr: String, passStr: String,id:Int) {
        println("=========================================")
        //http://10.0.2.2:5000/match/1 //android simulator should use 10.0.2.2 replace 127.0.0.1
        val request = Request.Builder()
            .url(requestURL+"user/$id")
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
                    val json = JSONObject(response.body!!.string())

//                    if (nameStr.isEmpty() && passStr.isEmpty()){
                        // user has correct emial and password go back to homescreen
                        println("Password correct")

                        val myIntent = Intent(applicationContext, MainActivity::class.java)
                        //return user json
                        myIntent.putExtra("user",json.toString())
                        startActivityForResult(myIntent, 0)
                        finish()
//                    }

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

