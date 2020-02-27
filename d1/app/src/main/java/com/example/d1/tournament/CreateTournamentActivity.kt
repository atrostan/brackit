package com.example.d1.tournament
import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.example.d1.MainActivity
import com.example.d1.R

class CreateTournamentActivity:AppCompatActivity(){

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.create_tournament)

        if (intent.hasExtra("json")){
            var text = findViewById<TextView>(R.id.textView)
            text.text = intent.getStringExtra("json")
        }
    }

    override fun onOptionsItemSelected(item: MenuItem?): Boolean {
        val myIntent = Intent(applicationContext, MainActivity::class.java)
        startActivityForResult(myIntent, 0)
        finish()
        return true
    }

}