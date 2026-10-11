import javax.tools.*;
import com.sun.source.util.JavacTask;
import java.nio.file.*;
import java.util.*;
public class SyntaxCheck {
 public static void main(String[] args) throws Exception {
  JavaCompiler c=ToolProvider.getSystemJavaCompiler();
  DiagnosticCollector<JavaFileObject> d=new DiagnosticCollector<>();
  try(StandardJavaFileManager fm=c.getStandardFileManager(d,Locale.ROOT,null)){
   List<java.io.File> files=new ArrayList<>();
   try(var stream=Files.walk(Path.of(args[0]))) {stream.filter(x->x.toString().endsWith(".java")).forEach(x->files.add(x.toFile()));}
   var units=fm.getJavaFileObjectsFromFiles(files);
   JavacTask task=(JavacTask)c.getTask(null,fm,d,List.of("-proc:none","--release","17"),null,units);
   task.parse();
   System.out.println("Parsed "+files.size()+" Java files, diagnostics: "+d.getDiagnostics().size());
   d.getDiagnostics().forEach(System.out::println);
   if(!d.getDiagnostics().isEmpty())System.exit(1);
  }
 }
}
