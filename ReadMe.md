Requirements:
    - Python 3+ (preferably 3.14.x)
    - Installing colorama using "pip install colorama"

Running the proxy:
    - In a terminal, navigate to the project directory:
        If not already in directory: cd '.\Proxy Caching Server\'
    - Run the proxy server using: "python proxy.py"
    - The server should start and display: "Proxy running on port 10000..."

Setting up the browser:
    - For example, we'll use firefox
    - Go to browser settings and search for "Proxy" and enter "Configure Proxy"
    - Select "Manual proxy configuration"
    - Set HTTP Proxy as "localhost" and port as "10000"
    - Enable the checkbox saying "Also use this proxy for HTTPS"
    - Now requests happening on the browser pass through our proxy

Requests using curl:
    - In a separate terminal (has to be command prompt not powershell to work)
    - HTTP request example: "curl --proxy http://localhost:10000 http://example.com"
    - HTTPS request example: "curl --proxy http://localhost:10000 https://example.com"