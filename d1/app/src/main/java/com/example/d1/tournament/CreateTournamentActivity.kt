package com.example.d1.tournament

import android.content.Intent
import android.content.pm.ActivityInfo
import android.os.Bundle
import android.text.InputType
import android.view.MenuItem
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.widget.ConstraintLayout
import com.example.d1.MainActivity
import com.example.d1.R
import com.example.d1.dao.Tournament
import com.example.d1.dao.User
import com.google.gson.Gson
import com.google.gson.JsonObject
import okhttp3.*
import java.io.IOException
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject


class CreateTournamentActivity:AppCompatActivity(){
    val requestURL = "http://10.0.2.2:5000/api/"
    //val requestURL = "http://172.20.10.2:5000/api/"
    var userString = "nouser"
    var TournamentID = 0
    var tournament_name = ""
    var teamName = arrayListOf<String>()
    var seeds = arrayListOf<Int>()
    lateinit var add:ImageView
    lateinit var edittext:EditText
    lateinit var teamlist:ListView
    lateinit var seedlist:ListView
    lateinit var finishBtn:Button
    var userName = ""
    var seed = 0
    lateinit var user:User
    lateinit var adapterTeam:ArrayAdapter<String>
    lateinit var adapterSeed:ArrayAdapter<Int>
    var LOBBYID = 0
    var USERNAME = ""
    var PASSWORD = ""
    var TOKEN = ""




    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.create_tournament)

        title = "Create Tournament"

        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT

        //navigate back
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        if (intent.hasExtra("user")){
            userString = intent.getStringExtra("user")
            var gson = Gson()
            user = gson.fromJson(userString,User::class.java)
            USERNAME = user.username
            PASSWORD = user.password_hash
            println("user login---------------"+userString)
        }

        if (intent.hasExtra("token")){
            TOKEN = intent.getStringExtra("token")
        }



        add = findViewById<ImageView>(R.id.add)
        edittext = findViewById<EditText>(R.id.editText)
        teamlist = findViewById<ListView>(R.id.team)
        seedlist = findViewById<ListView>(R.id.seed)
        finishBtn = findViewById<Button>(R.id.fBtn)

        adapterTeam = ArrayAdapter(this,android.R.layout.simple_list_item_1,teamName)
        teamlist.adapter = adapterTeam

        adapterSeed = ArrayAdapter(this,android.R.layout.simple_list_item_1,seeds)
        seedlist.adapter = adapterSeed
        adapterSeed.notifyDataSetChanged()
        adapterTeam.notifyDataSetChanged()

        add.setOnClickListener{
            if (!edittext.text.isEmpty()){
                if (edittext.hint == "Tournament Name"){
                    var tournamentName = findViewById<TextView>(R.id.tournmanetName)
                    tournament_name = edittext.text.toString()
                    tournamentName.text = tournament_name

                    edittext.hint = "Team Name"
                    edittext.setText("")

                    Thread{
                        createLobby()
                    }.start()


                }else if(edittext.hint == "Team Name"){
                    edittext.inputType = InputType.TYPE_CLASS_NUMBER

                    //temp user name for each add
                    userName = edittext.text.toString()
                    teamName.add(edittext.text.toString())

                    adapterTeam.notifyDataSetChanged()

                    edittext.hint = "Seed"
                    edittext.setText("")


                }else if(edittext.hint == "Seed"){
                    edittext.inputType = InputType.TYPE_CLASS_TEXT

                    //temp seed for each add
                    seed = edittext.text.toString().toInt()

                    seeds.add(edittext.text.toString().toInt())

                    adapterSeed.notifyDataSetChanged()

                    edittext.hint = "Team Name"
                    edittext.setText("")

                    Thread{
                        addUser(LOBBYID)
                    }.start()

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
                    createTournament(LOBBYID)
                    //getTournament(jobject)
                }.start()
            }
        }



    }


    fun createTournament(id:Int){
        val client = OkHttpClient.Builder().authenticator(object : Authenticator {
            @Throws(IOException::class)
            override fun authenticate(route: Route?, response: Response): Request? {
                if (response.request.header("Authorization") != null) {
                    return null // Give up, we've already attempted to authenticate.
                }
                println("Authenticating for response: $response")
                println("Challenges: ${response.challenges()}")

                val credential = Credentials.basic(TOKEN, "unused")
                return response.request.newBuilder()
                    .header("Authorization", credential)
                    .build()
            }
        }).build()


        val mediaType = "application/json; charset=utf-8".toMediaType()
        var jobject = JSONObject()

        val request = Request.Builder()
            .url(requestURL+"lobby/$id/create-tournament/")
            .post(jobject.toString().toRequestBody(mediaType))
            .build()

        client.newCall(request).execute().use { response ->
            //if (!response.isSuccessful) throw IOException("Unexpected code $response")

            if (response.code == 200){
                var tempjsonString = response.body!!.string()
                println("$tempjsonString-------------------------------")
                var objectjson = JSONObject(tempjsonString)
                var tId = objectjson["Success"].toString().split(" ")[2]
                println("$tId-------------------------------")
                TournamentID = tId.toInt()
                println("This is the TOURNAMENT ID=====================$TournamentID")

                runOnUiThread{
                    Toast.makeText(this@CreateTournamentActivity, "Tournament Created", Toast.LENGTH_SHORT).show()
                }

                val myIntent = Intent(applicationContext, MainActivity::class.java)
                myIntent.putExtra("user",userString)
                myIntent.putExtra("tId",TournamentID.toString())
                myIntent.putExtra("token",TOKEN)
                startActivityForResult(myIntent, 0)
                finish()
            }
        }
    }


    private fun createLobby(){
        val client = OkHttpClient.Builder().authenticator(object : Authenticator {
            @Throws(IOException::class)
            override fun authenticate(route: Route?, response: Response): Request? {
                if (response.request.header("Authorization") != null) {
                    return null // Give up, we've already attempted to authenticate.
                }
                println("Authenticating for response: $response")
                println("Challenges: ${response.challenges()}")

                val credential = Credentials.basic(TOKEN, "unused")
                return response.request.newBuilder()
                    .header("Authorization", credential)
                    .build()
            }
        }).build()


        val mediaType = "application/json; charset=utf-8".toMediaType()
        var jobject = JSONObject()
        jobject.put("tournament_name",tournament_name);

        val request = Request.Builder()
            .url(requestURL+"create/lobby/")
            .post(jobject.toString().toRequestBody(mediaType))
            .build()

        client.newCall(request).execute().use { response ->
            var tId = 0
            //if (!response.isSuccessful) throw IOException("Unexpected code $response")
            var temp = response.body!!.string()

            if (response.code == 201){
                var json = JSONObject(temp)
                LOBBYID = json["lobby_id"] as Int

                runOnUiThread{
                    Toast.makeText(this@CreateTournamentActivity,temp, Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun addUser(id:Int){
        val client = OkHttpClient.Builder().authenticator(object : Authenticator {
            @Throws(IOException::class)
            override fun authenticate(route: Route?, response: Response): Request? {
                if (response.request.header("Authorization") != null) {
                    return null // Give up, we've already attempted to authenticate.
                }
                println("Authenticating for response: $response")
                println("Challenges: ${response.challenges()}")

                val credential = Credentials.basic(TOKEN, "unused")
                return response.request.newBuilder()
                    .header("Authorization", credential)
                    .build()
            }
        }).build()


        val mediaType = "application/json; charset=utf-8".toMediaType()
        var jobject = JSONObject()
        jobject.put("username",userName);
        jobject.put("role","Guest")
        jobject.put("seed",seed)

        val request = Request.Builder()
            .url(requestURL+"lobby/$id/add-user/")
            .post(jobject.toString().toRequestBody(mediaType))
            .build()

        client.newCall(request).execute().use { response ->
            var tId = 0
            //if (!response.isSuccessful) throw IOException("Unexpected code $response")
            var temp = response.body!!.string()

            //add successful
            if (response.code == 202){
                var json = JSONObject(temp)

                runOnUiThread{
                    Toast.makeText(this@CreateTournamentActivity,temp, Toast.LENGTH_SHORT).show()
                }
            }else{
                runOnUiThread{
                    teamName.remove(userName)
                    seeds.remove(seed)
                    adapterSeed.notifyDataSetChanged()
                    adapterTeam.notifyDataSetChanged()
                    Toast.makeText(this@CreateTournamentActivity,temp, Toast.LENGTH_SHORT).show()
                }
            }
        }
    }


    override fun onOptionsItemSelected(item: MenuItem?): Boolean {
        val myIntent = Intent(applicationContext, MainActivity::class.java)
        myIntent.putExtra("user",userString)
        myIntent.putExtra("token",TOKEN)
        startActivityForResult(myIntent, 0)

        finish()
        return true
    }

}