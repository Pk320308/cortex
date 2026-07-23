// ==UserScript==
// @name         TheHive - Replace Wazuh → Astra (UI only)
// @namespace    http://example.local/
// @version      1.0
// @description  Replace visible "Wazuh" text with "Astra" in TheHive UI for display only
// @author       You
// @match        *://*/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // OPTIONAL: restrict to your TheHive host by editing the allowedHosts array
    const allowedHosts = ['host.docker.internal', 'localhost', 'thehive'];
    if(!allowedHosts.some(h => location.hostname.includes(h))) {
        // if not running on expected host, still continue if you want — comment out return
        // return;
    }

    const findText = 'Wazuh';
    const replaceText = 'Astra';
    const re = new RegExp(findText, 'g');

    // Intercept fetch responses for TheHive alerts API and replace occurrences in JSON
    (function interceptFetch(){
        if(!window.fetch) return;
        const origFetch = window.fetch.bind(window);
        window.fetch = function(resource, init){
            const url = (typeof resource === 'string') ? resource : (resource && resource.url) || '';
            return origFetch(resource, init).then(async res => {
                try{
                    if(!url.includes('/api/alert')) return res;
                    const cloned = res.clone();
                    const data = await cloned.json().catch(()=>null);
                    if(!data) return res;

                    function replaceRec(v){
                        if(typeof v === 'string') return v.replace(/Wazuh/g, 'Astra');
                        if(Array.isArray(v)) return v.map(replaceRec);
                        if(v && typeof v === 'object'){
                            const out = {};
                            for(const k of Object.keys(v)) out[k] = replaceRec(v[k]);
                            return out;
                        }
                        return v;
                    }

                    const newData = replaceRec(data);
                    const body = JSON.stringify(newData);
                    const headers = new Headers(res.headers);
                    headers.set('content-length', String(new TextEncoder().encode(body).length));
                    return new Response(body, { status: res.status, statusText: res.statusText, headers });
                }catch(e){
                    return res;
                }
            });
        };
        console.log('Fetch interceptor installed for /api/alert (Wazuh → Astra)');
    })();

    // DOM fallback: replace visible text nodes
    function replaceInTextNode(node){
        try{
            if(node.nodeType === Node.TEXT_NODE && re.test(node.nodeValue)){
                node.nodeValue = node.nodeValue.replace(re, replaceText);
            }
        }catch(e){/* ignore */}
    }

    function replaceAll(){
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
        let node;
        while(node = walker.nextNode()){
            replaceInTextNode(node);
        }
    }

    replaceAll();
    const mo = new MutationObserver(() => replaceAll());
    mo.observe(document.body, { childList: true, subtree: true, characterData: true });

    console.log('TheHive UI replacer active: "' + findText + '" → "' + replaceText + '"');
})();
