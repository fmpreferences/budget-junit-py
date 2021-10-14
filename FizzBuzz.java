import java.util.Scanner;

/**
 * sample class
 */
public class FizzBuzz {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int i;
        do {
            System.out.print("number? ");
            i = scanner.nextInt();
            scanner.nextLine();
            if (i % 15 == 0) {
                System.out.println("FizzBuzz");
            } else if (i % 5 == 0) {
                System.out.println("Buzz");
            } else if (i % 3 == 0) {
                System.out.println("Fizz");
            } else {
                System.out.println(i);
            }
        } while (i >= 0);
        scanner.close();
    }
}
