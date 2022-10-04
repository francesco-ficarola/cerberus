 # Cerberus Stress Testing Tool
 
<img  src="https://img.shields.io/badge/Python-3.8-blue">  <img  src="https://img.shields.io/badge/Licence-MIT-yellowgreen">

**Cerberus is another basic stressing tool simulating DDoS attacks, written in Python.**

You may use Cerberus for educational purposes or for testing the robusteness of your IT infrastructure and your web applications resilience. These kind of tests allows you to further fine-tune your security posture.

Please note that Cerberus is not designed to perform illegal activities, so **do not commit criminal acts**. By using this software, you agree to take full responsability for any damage caused by an irregulare practice of Cerberus.

![cerberus](https://user-images.githubusercontent.com/1279595/193843080-009b3380-4aa3-44d6-9329-c2a18f91801a.png)

Watch a demo here: https://youtu.be/EB6zVtHVjXk

## Some technical details and considerations

Yes, I know. The wording _DDoS_ is not correct since a DDoS attack is carried out from several sources (e.g. a botnet).  However, I decided to use the _DDoS_ word in the Cerberus description precisely because I wanted to emphasize you can use this software from multiple devices to simulate a DDoS attack (please try on authorized resources only).

### Supported operating systems

I successfully tested Cerberus on Ubuntu and Debian, so likely you won't have any issue in Deb-based distributions. If you would like to contribute, please test on Arch Linux and on other RPM-based distributions, then let me know if Cerberus properly works.

Cerberus can be executed on Windows as well (just install dependencies), but you have to _unlock_ the equivalent Linux "ulimit" values (is that feasible? I don't know) to send a lot of simultaneous requests.

### What are the available options?

By default Cerberus runs by using this values:

* Total requests = 10000
* Concurrent requests = 3000
* Port = 443 (HTTPS)
* SSL = enabled
* HTTP method = GET
* Response timeout = 120 seconds
* Referer = example.com
* Verbose = disabled
* Block size = 8192 bytes

You can change all of the above parameters, depending on the _use-case_ you are testing.

For instance, you may test a pre-production application running on port tcp/80, so you need to disable the SSL encryption as well as to enable the verbose mode:

    --port 80 --no-ssl --verbose

Another good practice is to change the referer parameter by entering a valid value (e.g. google.com):

    --referer google.com

If you'd like to test a web application using a login form, then change the method parameter with POST, modify the path (if needed) and add a valid data input in JSON format.

    --method post --path '/login' --data '{"user":"admin", "password":"test"}'

### Cache and headers

In order to avoid cached responses by the targeted web server, headers are configured in the following way:

    Cache-Control: no-cache, no-store, must-revalidate
    Pragma: no-cache
    Expires: 0
    Connection: keep-alive

However, in many cases that configuration is not sufficient (e.g. for platforms using Varnish), so each request is sent to a default path '/' (that can be changed) followed by a random string, for instance:

    ?djwzms=X

where _X_ is the number of the current request. This kind of requests increase the possibility to receive a "fresh" response from the web server. In doing so, the system needs to process the full request, adding more computation load on the server.

## Warning and License

Cerberus can damage the targeted system since it can overload CPUs and RAM, so please be careful and proceed step by step.

MIT (c) 2022 - Francesco Ficarola
