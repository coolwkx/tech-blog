(function(root){
 'use strict';
 function validate(data){
  if(!data||Array.isArray(data)||data.version!==2||!data.records||typeof data.records!=='object'||Array.isArray(data.records))throw Error('不是本站支持的版本 2 学习记录文件。');
  const entries=Object.entries(data.records);if(entries.length>10000)throw Error('记录数量超过限制。');
  const records=Object.create(null);
  for(const [id,value] of entries){
   if(!/^[a-zA-Z0-9-]{1,100}$/.test(id)||['constructor','prototype','__proto__'].includes(id)||!value||typeof value!=='object'||Array.isArray(value))throw Error('记录编号或内容无效。');
   const record={};
   if(value.status!==undefined){if(!['learning','review','mastered'].includes(value.status))throw Error('学习状态无效。');record.status=value.status;}
   if(value.bookmarked!==undefined){if(typeof value.bookmarked!=='boolean')throw Error('收藏标记无效。');record.bookmarked=value.bookmarked;}
   if(value.note!==undefined){if(typeof value.note!=='string'||value.note.length>50000)throw Error('个人笔记内容无效或过长。');record.note=value.note;}
   for(const field of ['position','scrollY','visitedAt','updatedAt'])if(value[field]!==undefined){if(typeof value[field]!=='number'||!Number.isFinite(value[field])||value[field]<0||(field==='position'&&value[field]>100))throw Error('阅读位置或时间无效。');record[field]=value[field];}
   records[id]=record;
  }
  const preferences={};const input=data.preferences||{};
  if(input.theme!==undefined){if(!['dark','light'].includes(input.theme))throw Error('主题设置无效。');preferences.theme=input.theme;}
  if(input.fontSize!==undefined){const value=Number(input.fontSize);if(![16,18,20].includes(value))throw Error('字号设置无效。');preferences.fontSize=value;}
  if(input.lineHeight!==undefined){const value=Number(input.lineHeight);if(![1.75,1.95,2.2].includes(value))throw Error('行距设置无效。');preferences.lineHeight=value;}
  const last=typeof data.last==='string'&&/^[a-zA-Z0-9-]{1,100}$/.test(data.last)?data.last:null;
  return {records,preferences,last};
 }
 function restore(current,incoming,mode){
  if(!['merge','replace'].includes(mode))throw Error('恢复方式无效。');
  const imported=validate(incoming);
  return mode==='replace'?imported:{records:{...current.records,...imported.records},preferences:{...current.preferences,...imported.preferences},last:imported.last||current.last};
 }
 root.WKXRecords={validate,restore};
 if(typeof module==='object'&&module.exports)module.exports=root.WKXRecords;
})(typeof globalThis==='object'?globalThis:this);
