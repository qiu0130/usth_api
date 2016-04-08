package com.example.qiu.usthapp;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;


public class LoginActivity extends AppCompatActivity {


    private Button login_bt;
    private EditText userName, passWord;
    private String user_text, password_text;

    private String TAG = "login";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);


        login_bt = (Button) findViewById(R.id.login_bt);
        passWord = (EditText) findViewById(R.id.password_et);
        userName = (EditText) findViewById(R.id.name_et);


        login_bt.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                user_text = userName.getText().toString();
                password_text = passWord.getText().toString();

                if (user_text.equals("") || password_text.equals("")) {

                    Toast.makeText(getApplicationContext(), "密码或者账号不能为空", Toast.LENGTH_LONG).show();
                    return;
                }
                Intent intent = new Intent(LoginActivity.this, MainActivity.class);

                intent.putExtra("name", user_text);
                intent.putExtra("passw", password_text);

                startActivity(intent);

            }
        });

    }



    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }





}
