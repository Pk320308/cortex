Replace Wazuh → Astra (UI-only)
================================

This userscript replaces visible occurrences of the word `Wazuh` with `Astra` in the browser UI only.
It does NOT change any backend data or TheHive database.

Install
-------
1. Install Tampermonkey (Chrome/Edge/Firefox) or Greasemonkey (Firefox).
2. Create a new userscript and paste the contents of `scripts/replace_wazuh.user.js`.
3. Optionally edit the `allowedHosts` array in the script to restrict the script to your TheHive host.

Quick test (console)
--------------------
If you prefer a one-off test, open the browser console on the TheHive page and paste:

```javascript
(function replaceWazuh(){
  const re = /Wazuh/g;
  function walk(n){
    if(n.nodeType===3){ if(re.test(n.nodeValue)) n.nodeValue = n.nodeValue.replace(re,'Astra'); }
    else for(let c of n.childNodes) walk(c);
  }
  walk(document.body);
  const mo = new MutationObserver(()=>walk(document.body));
  mo.observe(document.body,{childList:true,subtree:true,characterData:true});
  console.log('Replace active: Wazuh → Astra');
})();
```

Notes
-----
- This approach is reversible and safe for testing.
- To make changes visible to other users, either share the userscript or implement a server-side transform (recommended non-destructive approach: add `source_alias` or a tag).
