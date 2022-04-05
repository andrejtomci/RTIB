# rewrite_redirector
Setups *apache2 mod_rewrite* redirector.

If the request doesn't match the expected *URI* and *user_agent*, it is redirected to a legitimate address.

# Arguments
**uri**: expected URI  
**user_agent**: expected user agent  
**redirect_to**: destination address/name of the other infrastructure component  
**invalid_traffic**: legitimate address, in case the request URI/user-agent don't match the expected