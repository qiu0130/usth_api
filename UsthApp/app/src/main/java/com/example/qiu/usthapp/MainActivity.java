package com.example.qiu.usthapp;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.drawable.AnimationDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseExpandableListAdapter;
import android.widget.ExpandableListView;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;


public class MainActivity extends Activity{

    public String TAG  = "main";

    private String url = "http://usth.applinzi.com/api";
    private ExpandableListView expandableListView;

    private ImageView imageView;
    private AnimationDrawable ad;
    private TextView title_tv;

    private List<String> group_list;
    private ArrayList<List<String>> item_list;
    private ArrayList<String> item_lt;


    private String name;
    private String passw;

    private JSONObject jsonObject;


    public static int IS_PASS = 3;
    public static int IS_FAIL = 2;
    public static int IS_SEMESTER = 1;

    private boolean fail_flag;
    private boolean semester_flag;
    private boolean passing_flag;


    private Handler handler = new Handler() {

        @Override
        public void handleMessage(Message msg) {

            String  data = (String)msg.obj;

           if (msg.what == IS_FAIL) {

               fail_flag = fail_cover_json(data);
            }

            if (msg.what == IS_PASS) {
               passing_flag =  passing_cover_json(data);
            }

            if (msg.what == IS_SEMESTER) {
                semester_flag = semester_coverJson(data);
            }
             //    加载数据

            Log.d(TAG, "检查 flag");
            Log.d(TAG, "semester = " + semester_flag + ",fail = " + fail_flag + ",passing = " + passing_flag);
//
//            if (!semester_flag) {
//
//                startActivity(new Intent(MainActivity.this, LoginActivity.class));
//            }
//            if (!fail_flag) {
//                startActivity(new Intent(MainActivity.this, LoginActivity.class));
//            }
//            if (!passing_flag) {
//                startActivity(new Intent(MainActivity.this, LoginActivity.class));
//            }

            if (semester_flag || fail_flag || passing_flag) {

                imageView.setVisibility(View.GONE);
                expandableListView.setAdapter(new MyExpandableListViewAdapter(MainActivity.this));
               // expandableListView.expandGroup(0); // 默认展开第一项
            }



        }
    };


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


            title_tv = (TextView) findViewById(R.id.tv_lost);
            imageView = (ImageView) findViewById(R.id.imageView);
            ad = (AnimationDrawable)imageView.getDrawable();

            imageView.postDelayed(new Runnable() {
            @Override
            public void run() {
                ad.run();
                }
            }, 0);


          Intent intent = getIntent();
          name = intent.getStringExtra("name");
          passw = intent.getStringExtra("passw");


         item_list = new ArrayList<List<String>>();
         group_list = new ArrayList<String>();


            RequestData("semester", 1);
            RequestData("fail", 2);
            RequestData("passing", 3);



        expandableListView = (ExpandableListView)findViewById(R.id.content_exp_lv);
        expandableListView.setGroupIndicator(null);

        // 监听组点击
        expandableListView.setOnGroupClickListener(new ExpandableListView.OnGroupClickListener() {
            @SuppressLint("NewApi")
            @Override
            public boolean onGroupClick(ExpandableListView parent, View v, int groupPosition, long id) {
                if (item_list.get(groupPosition).isEmpty()) {
                    return true;
                }
                return false;
            }
        });

        // 监听每个分组里子控件的点击事件
        expandableListView.setOnChildClickListener(new ExpandableListView.OnChildClickListener() {

            @Override
            public boolean onChildClick(ExpandableListView parent, View v, int groupPosition, int childPosition, long id) {

                Toast.makeText(MainActivity.this, item_list.get(groupPosition).get(childPosition), Toast.LENGTH_SHORT).show();
                return false;
            }
        });

    }

    private boolean passing_cover_json(String response) {

        try {
            jsonObject = new JSONObject(response);
            if (jsonObject.getString("status").equals("error")) {

                Toast.makeText(this, jsonObject.getString("cause"), Toast.LENGTH_SHORT).show();
                imageView.setVisibility(View.GONE);
               // startActivity(new Intent(MainActivity.this, LoginActivity.class));
                return false;
            }

            JSONArray array =  jsonObject.getJSONArray("semeters");
            title_tv.setText(jsonObject.getString("_name") + "成绩单");

            for (int i = 0; i < array.length(); i++) {
                String tmp = (String) array.get(i);
                group_list.add(tmp + "学期");

                JSONArray array1 = jsonObject.getJSONArray(tmp);
                item_lt = new ArrayList<String>();


                if (array1.length() > 0 && array1!= null) {
                    for (int j = 0; j < array1.length(); j++) {
                        JSONObject obj = array1.getJSONObject(j);

                        String tmps  = "课程: "+ obj.getString("course_name") + "\n"
                                +  "成绩: " + obj.getString("socre") + "\n"
                                + "学分: "+ obj.getString("credit") + "\n"
                                + "课程性质: " + obj.getString("course_attribute");
                        item_lt.add(tmps);
                    }
                } else {
                       item_lt.add("无");
                }
                item_list.add(item_lt);
            }


        } catch (JSONException e) {
            e.printStackTrace();
        }

        return true;

    }
    private boolean fail_cover_json(String response) {

        try {


           // Log.d(TAG, response);

             jsonObject = new JSONObject(response);
             if (jsonObject.getString("status").equals("error")) {

                Toast.makeText(this, jsonObject.getString("cause"), Toast.LENGTH_SHORT).show();
                 imageView.setVisibility(View.GONE);
                // startActivity(new Intent(MainActivity.this, LoginActivity.class));
                return false;
             }

            group_list.add("曾不及格");
            title_tv.setText(jsonObject.getString("_name") + "成绩单");
            JSONArray array = jsonObject.getJSONArray("ever_fail_grade");
            item_lt = new ArrayList<String>();

            if (array.length() > 0) {
                for (int i = 0; i < array.length(); i++) {
                    JSONObject obj = array.getJSONObject(i);
                    String tmp  = "课程: "+ obj.getString("course_name") + "\n"
                            +  "成绩: " + obj.getString("socre") + "\n"
                            + "学分: "+ obj.getString("credit") + "\n"
                            + "课程性质: " + obj.getString("course_attribute");
                    item_lt.add(tmp);
                }
                item_list.add(item_lt);

            }else {
                item_lt.add("无");
                item_list.add(item_lt);

            }

            group_list.add("尚不及格");
            item_lt = new ArrayList<String>();
            JSONArray array1 = jsonObject.getJSONArray("yet_fail_grade");
            if (array1.length() > 0) {
                for (int i = 0; i < array1.length(); i++) {

                    JSONObject obj = array1.getJSONObject(i);
                    String tmp  = "课程: "+ obj.getString("course_name") + "\n"
                            +  "成绩: " + obj.getString("socre") + "\n"
                            + "学分: "+ obj.getString("credit") + "\n"
                            + "课程性质: " + obj.getString("course_attribute");
                    item_lt.add(tmp);
                }
                item_list.add(item_lt);

            } else {

                item_lt.add("无");
                item_list.add(item_lt);
            }

         } catch (JSONException e) {
            e.printStackTrace();
        }

        return true;

    }

    private boolean semester_coverJson(String response) {

        try {

           // Log.d(TAG, response);

            JSONObject jsonObject =  new JSONObject(response);

            String status= jsonObject.getString("status");

            if (status.equals("error")) {
                Toast.makeText(this, jsonObject.getString("cause"), Toast.LENGTH_SHORT).show();
                //startActivity(new Intent(MainActivity.this, LoginActivity.class));
                imageView.setVisibility(View.GONE);
               return false;
            }

            group_list.add("本学期");
            title_tv.setText(jsonObject.getString("_name") + "成绩单");
            item_lt = new ArrayList<String>();

            if (status.equals("ok")) {

                JSONArray array = jsonObject.getJSONArray("this_semester_grade");
                if (array != null) {

                    for (int i = 0; i < array.length(); i++) {

                        JSONObject obj = array.getJSONObject(i);

                        String tmp  = "课程: "+ obj.getString("course_name") + "\n"
                                  +  "成绩: " + obj.getString("socre") + "\n"
                                  + "学分: "+ obj.getString("credit") + "\n"
                                 + "课程性质: " + obj.getString("course_attribute");

                        item_lt.add(tmp);
                    }
                    item_list.add(item_lt);

                }
            } else {

                item_lt.add("无");
                item_list.add(item_lt);

            }

        } catch (JSONException e) {
            e.printStackTrace();
        }

        return true;
    }


    private void RequestData(final String datType, final  int id) {

        new Thread(new Runnable() {
            @Override
            public void run() {

                HttpURLConnection conn = null;

                try {
                    // 创建一个URL对象
                    URL mURL = new URL(url);
                    // 调用URL的openConnection()方法,获取HttpURLConnection对象
                    conn = (HttpURLConnection) mURL.openConnection();

                    conn.setRequestMethod("POST");  // 设置请求方法为post
                    //  conn.setReadTimeout(5000);// 设置读取超时为5秒
                    //   conn.setConnectTimeout(10000);// 设置连接网络超时为10秒
                    conn.setDoOutput(true);// 设置此方法,允许向服务器输出内容

                    // post请求的参数

                    String data = "username=" + name + "&password=" + passw+ "&type=" + datType;
                    // 获得一个输出流,向服务器写数据,默认情况下,系统不允许向服务器输出内容
                    OutputStream out = conn.getOutputStream();// 获得一个输出流,向服务器写数据
                    out.write(data.getBytes());
                    out.flush();
                    out.close();

                    int responseCode = conn.getResponseCode();// 调用此方法就不必再使用conn.connect()方法
                    if (responseCode == 200) {

                        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                        String line = "";
                        StringBuilder responseOutput = new StringBuilder();

                        while((line = br.readLine()) != null ) {
                            responseOutput.append(line);
                        }
                        br.close();


                      //  Log.d(TAG, responseOutput.toString());

                        // 获取一个Message对象，设置what为1
                        Message msg = Message.obtain();
                        msg.obj = responseOutput.toString();
                        msg.what = id;
                        // 发送这个消息到消息队列中
                        handler.sendMessage(msg);

                    } else {
                        Log.d(TAG, "访问失败: " + responseCode);
                    }

                } catch (Exception e) {
                    e.printStackTrace();
                } finally {
                    if (conn != null) {
                        conn.disconnect();// 关闭连接
                    }
                }
            }
        }).start();

    }

    // 用过ListView的人一定很熟悉，只不过这里是BaseExpandableListAdapter
    class MyExpandableListViewAdapter extends BaseExpandableListAdapter {

        private Context context;

        public MyExpandableListViewAdapter(Context context)
        {
            this.context = context;
        }

        /**
         *
         * 获取组的个数
         *
         * @return
         * @see android.widget.ExpandableListAdapter#getGroupCount()
         */
        @Override
        public int getGroupCount()
        {
            return group_list.size();
        }

        /**
         *
         * 获取指定组中的子元素个数
         *
         * @param groupPosition
         * @return
         * @see android.widget.ExpandableListAdapter#getChildrenCount(int)
         */
        @Override
        public int getChildrenCount(int groupPosition)
        {
            return item_list.get(groupPosition).size();
        }

        /**
         *
         * 获取指定组中的数据
         *
         * @param groupPosition
         * @return
         * @see android.widget.ExpandableListAdapter#getGroup(int)
         */
        @Override
        public Object getGroup(int groupPosition)
        {
            return group_list.get(groupPosition);
        }

        /**
         *
         * 获取指定组中的指定子元素数据。
         *
         * @param groupPosition
         * @param childPosition
         * @return
         * @see android.widget.ExpandableListAdapter#getChild(int, int)
         */
        @Override
        public Object getChild(int groupPosition, int childPosition)
        {
            return item_list.get(groupPosition).get(childPosition);
        }

        /**
         *
         * 获取指定组的ID，这个组ID必须是唯一的
         *
         * @param groupPosition
         * @return
         * @see android.widget.ExpandableListAdapter#getGroupId(int)
         */
        @Override
        public long getGroupId(int groupPosition)
        {
            return groupPosition;
        }

        /**
         *
         * 获取指定组中的指定子元素ID
         *
         * @param groupPosition
         * @param childPosition
         * @return
         * @see android.widget.ExpandableListAdapter#getChildId(int, int)
         */
        @Override
        public long getChildId(int groupPosition, int childPosition)
        {
            return childPosition;
        }

        /**
         *
         * 组和子元素是否持有稳定的ID,也就是底层数据的改变不会影响到它们。
         *
         * @return
         * @see android.widget.ExpandableListAdapter#hasStableIds()
         */
        @Override
        public boolean hasStableIds()
        {
            return true;
        }

        /**
         *
         * 获取显示指定组的视图对象
         *
         * @param groupPosition 组位置
         * @param isExpanded 该组是展开状态还是伸缩状态
         * @param convertView 重用已有的视图对象
         * @param parent 返回的视图对象始终依附于的视图组
         * @return
         * @see android.widget.ExpandableListAdapter#getGroupView(int, boolean, android.view.View,
         *      android.view.ViewGroup)
         */
        @Override
        public View getGroupView(int groupPosition, boolean isExpanded, View convertView, ViewGroup parent)
        {
            GroupHolder groupHolder = null;
            if (convertView == null)
            {
                convertView = LayoutInflater.from(context).inflate(R.layout.expendlist_group, null);
                groupHolder = new GroupHolder();
                groupHolder.group_tv = (TextView)convertView.findViewById(R.id.group_tv);
                convertView.setTag(groupHolder);
            }
            else
            {
                groupHolder = (GroupHolder)convertView.getTag();
            }

            groupHolder.group_tv.setText(group_list.get(groupPosition));
            return convertView;
        }


        /**
         *
         * 获取一个视图对象，显示指定组中的指定子元素数据。
         *
         * @param groupPosition 组位置
         * @param childPosition 子元素位置
         * @param isLastChild 子元素是否处于组中的最后一个
         * @param convertView 重用已有的视图(View)对象
         * @param parent 返回的视图(View)对象始终依附于的视图组
         * @return
         * @see android.widget.ExpandableListAdapter#getChildView(int, int, boolean, android.view.View,
         *      android.view.ViewGroup)
         */
        @Override
        public View getChildView(int groupPosition, int childPosition, boolean isLastChild, View convertView, ViewGroup parent)
        {
            ItemHolder itemHolder = null;
            if (convertView == null)
            {
                convertView = LayoutInflater.from(context).inflate(R.layout.expendlist_item, null);
                itemHolder = new ItemHolder();
                itemHolder.content_tv = (TextView)convertView.findViewById(R.id.content_tv);

                convertView.setTag(itemHolder);
            }
            else
            {
                itemHolder = (ItemHolder)convertView.getTag();
            }

            String tmp = item_list.get(groupPosition).get(childPosition);
            String[] list_tmp = tmp.split("\n");

            if (list_tmp.length > 3) {

                tmp = list_tmp[0].split(":")[1] + " " + list_tmp[1].split(":")[1];
            }else {
                tmp = "无";
            }


            itemHolder.content_tv.setText(tmp);

            return convertView;
        }

        /**
         *
         * 是否选中指定位置上的子元素。
         *
         * @param groupPosition
         * @param childPosition
         * @return
         * @see android.widget.ExpandableListAdapter#isChildSelectable(int, int)
         */
        @Override
        public boolean isChildSelectable(int groupPosition, int childPosition)
        {
            return true;
        }

    }

    class GroupHolder
    {
        public TextView group_tv;
    }

    class ItemHolder
    {

        public TextView content_tv;
    }




}