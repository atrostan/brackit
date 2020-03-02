package com.example.d1.tournament

import android.content.Intent
import android.os.Bundle
import android.text.InputType
import android.view.MenuItem
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.widget.ConstraintLayout
import com.example.d1.MainActivity
import com.example.d1.R
import com.example.d1.dao.Tournament
import com.google.gson.Gson
import okhttp3.*
import java.io.IOException
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject


class CreateTournamentActivity:AppCompatActivity(){
    var userString = "nouser"


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.create_tournament)

        var tournament_name = ""
        var teamName = arrayListOf<String>()
        var seeds = arrayListOf<Int>()



        //navigate back
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        if (intent.hasExtra("user")){
            userString = intent.getStringExtra("user")
            println("user login---------------"+userString)
        }

        var add = findViewById<ImageView>(R.id.add)
        var edittext = findViewById<EditText>(R.id.editText)
        var teamlist = findViewById<ListView>(R.id.team)
        var seedlist = findViewById<ListView>(R.id.seed)
        var constraint = findViewById<ConstraintLayout>(R.id.constraint)
        var finishBtn = findViewById<Button>(R.id.fBtn)

        var adapterTeam = ArrayAdapter(this,android.R.layout.simple_list_item_1,teamName)

        teamlist.adapter = adapterTeam
        var adapterSeed = ArrayAdapter(this,android.R.layout.simple_list_item_1,seeds)
        seedlist.adapter = adapterSeed

        add.setOnClickListener{
            if (!edittext.text.isEmpty()){
                if (edittext.hint == "Tournament Name"){
                    var tournamentName = findViewById<TextView>(R.id.tournmanetName)
                    tournament_name = edittext.text.toString()
                    tournamentName.text = tournament_name

                    edittext.hint = "Team Name"
                    edittext.setText("")

                }else if(edittext.hint == "Team Name"){
                    edittext.inputType = InputType.TYPE_CLASS_NUMBER
                    teamName.add(edittext.text.toString())

                    adapterTeam.notifyDataSetChanged()

                    edittext.hint = "Seed"
                    edittext.setText("")


                }else if(edittext.hint == "Seed"){
                    edittext.inputType = InputType.TYPE_CLASS_TEXT
                    seeds.add(edittext.text.toString().toInt())

                    adapterSeed.notifyDataSetChanged()

                    edittext.hint = "Team Name"
                    edittext.setText("")
                }
            }

        }

        teamlist.setOnItemLongClickListener { parent, view, position, id ->
            var s = teamName.get(position)
            teamName.remove(s)
            var i = seeds.get(position)
            seeds.remove(i)
            adapterSeed.notifyDataSetChanged()
            adapterTeam.notifyDataSetChanged()
            true
        }

        seedlist.setOnItemClickListener{parent, view, position, id ->
            var s = teamName.get(position)
            teamName.remove(s)
            var i = seeds.get(position)
            seeds.remove(i)
            adapterSeed.notifyDataSetChanged()
            adapterTeam.notifyDataSetChanged()
            true
        }

        finishBtn.setOnClickListener{


            if (!tournament_name.isEmpty() && !teamName.isEmpty() && !seeds.isEmpty()){
                val t = Tournament(teamName,seeds,tournament_name)
                var gson = Gson()
                val jsonString = Gson().toJson(t)
                var jobject = JSONObject(jsonString)

                println("jsonString-------------"+jsonString)

                Thread {
                    //Do some Network Request
                    getTournament(jobject)
                }.start()


            }
        }



    }

    fun getTournament(jobject:JSONObject){

        val client = OkHttpClient.Builder().authenticator(object : Authenticator {
            @Throws(IOException::class)
            override fun authenticate(route: Route?, response: Response): Request? {
                if (response.request.header("Authorization") != null) {
                    return null // Give up, we've already attempted to authenticate.
                }
                println("Authenticating for response: $response")
                println("Challenges: ${response.challenges()}")

                val credential = Credentials.basic("miguel", "python")
                return response.request.newBuilder()
                    .header("Authorization", credential)
                    .build()
            }
        })
            .build()


        val mediaType = "application/json; charset=utf-8".toMediaType()

        val request = Request.Builder()
            .url("http://172.17.184.246:5000/api/created-tournaments/")
            .post(jobject.toString().toRequestBody(mediaType))
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response")

            println(response.body!!.string()+"---------------post tournament")
        }
    }


    override fun onOptionsItemSelected(item: MenuItem?): Boolean {
        val myIntent = Intent(applicationContext, MainActivity::class.java)
        myIntent.putExtra("user",userString)
        startActivityForResult(myIntent, 0)

        finish()
        return true
    }

}